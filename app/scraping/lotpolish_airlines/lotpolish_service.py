from datetime import datetime
from airlines_main.utility import generate_numeric_uuid
from app.scraping.services.mongo_service import MongoService


class LotPolishIngestionService:

    def __init__(self, raw_data: dict, ci_id):
        self.raw   = raw_data
        self.data  = raw_data.get("data", raw_data)
        self.air   = self.data.get("air", {})
        self.ci_id = str(ci_id)

        # Dictionaries block — used for code → name lookups
        self.dicts = raw_data.get("dictionaries", {})

        mongo = MongoService()
        self.raw_col    = mongo.get_collection("airlines_raw_data")
        self.header_col = mongo.get_collection("header_info")
        self.pax_col    = mongo.get_collection("pax_info")
        self.flight_col = mongo.get_collection("flight_info")
        self.fare_col   = mongo.get_collection("fare_info")

    # =========================================================
    # MAIN INGEST
    # =========================================================

    def ingest(self):
        pnr       = self.data.get("ibeOrderId")
        last_name = self._extract_last_name()

        self._store_raw_data(pnr, last_name)

        header_doc  = self._build_header(pnr, last_name)
        pax_docs    = self._build_pax(pnr, last_name)
        flight_docs = self._build_flight(pnr, last_name)
        fare_docs   = self._build_fare(pnr, last_name)

        header_id  = self.header_col.insert_one(header_doc).inserted_id
        pax_ids    = [self.pax_col.insert_one(p).inserted_id    for p in pax_docs]
        flight_ids = [self.flight_col.insert_one(f).inserted_id for f in flight_docs]
        fare_ids   = [self.fare_col.insert_one(f).inserted_id   for f in fare_docs]

        return {
            "ci_id":     self.ci_id,
            "pnr":       pnr,
            "last_name": last_name,
            "inserted_ids": {
                "header": str(header_id),
                "pax":    [str(i) for i in pax_ids],
                "flight": [str(i) for i in flight_ids],
                "fare":   [str(i) for i in fare_ids],
            },
        }

    # =========================================================
    # 1. RAW DATA
    # =========================================================

    def _store_raw_data(self, pnr, last_name):
        """
        Collection : airlines_raw_data
        Stores the complete unmodified API response.
        """
        self.raw_col.insert_one({
            "ci_id":      self.ci_id,
            "airline":    "LotPolish",
            "is_deleted": False,
            "pnr":        pnr,
            "last_name":  last_name,
            "raw_data":   self.raw,
            "created_at": datetime.utcnow(),
        })

    # =========================================================
    # 2. HEADER  (one doc per booking)
    # =========================================================

    def _build_header(self, pnr, last_name):
        """
        Collection : header_info

        LOT-specific notes:
        - Root key is 'data', pricing lives in data.air.prices.totalPrices
        - data.ibeOrderId is the PNR / booking reference
        - Warnings block at root level (e.g. FLIGHT DISRUPTION, MISSING EMAIL)
        - orderEligibilities block covers cancel, change, refund, nameChange eligibility
        - servicingAllowance block covers what actions are permitted in the UI
        - additionalInfo block carries market, currency, offline/NDC flags
        - plugradeEligibility carries upgrade/seat upsell offer URLs
        - ticketIssueDate at data level
        """
        total_prices = self.air.get("prices", {}).get("totalPrices", [])
        total        = total_prices[0] if total_prices else {}

        order_elig   = self.data.get("orderEligibilities", {})

        each_ci_id = generate_numeric_uuid()

        return {
            "parent_ci_id": self.ci_id,
            "ci_id":        each_ci_id,
            "airline":      "LotPolish",
            "is_deleted":   False,

            "pnr":       pnr,
            "last_name": last_name,

            # Booking metadata
            "ibe_flow_id":       self.raw.get("ibeFlowId"),
            "ticket_issue_date": self.data.get("ticketIssueDate"),

            # Warnings (disruption / missing contact alerts)
            "warnings": self.raw.get("warnings", []),
            "errors":   self.raw.get("errors", []),

            # Total booking price
            "total_price": {
                "total":    total.get("total", {}).get("value"),
                "base":     total.get("base", {}).get("value"),
                "taxes":    total.get("totalTaxes", {}).get("value"),
                "currency": total.get("total", {}).get("currencyCode"),
            },

            # Eligibilities
            "cancel_eligibility":        order_elig.get("cancel", {}),
            "cancel_refund_eligibility": order_elig.get("cancelAndRefund", {}),
            "change_eligibility":        order_elig.get("change", []),
            "name_change_eligibility":   order_elig.get("nameChange", {}),
            "seat_change_eligibility":   order_elig.get("seatChange", []),
            "service_change_eligibility":order_elig.get("serviceChange", []),
            "acknowledge_eligibility":   order_elig.get("acknowledge", []),
            "flight_reaccommodation":    order_elig.get("flightReaccommodation", {}),

            # Servicing permissions
            "servicing_allowance": self.data.get("servicingAllowance", {}),

            # Additional flags (market, currency, NDC, offline, etc.)
            "additional_info": self.data.get("additionalInfo", {}),

            # Upsell / upgrade offers
            "plugrade_eligibility": self.data.get("plugradeEligibility", {}),

            # Insurance
            "insurance_eligibility": self.data.get("insuranceEligibility", {}),

            # Group / no-show flags
            "is_group_booking":             self.data.get("isGroupBooking"),
            "is_booking_impacted_by_no_show": self.data.get("isBookingImpactedByNoShow"),

            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

    # =========================================================
    # 3. PASSENGERS  (one doc per passenger)
    # =========================================================

    def _build_pax(self, pnr, last_name):
        """
        Collection : pax_info

        LOT-specific notes:
        - Passengers live in data.travelers
        - Each traveler has: id, name{firstName, lastName, title},
          passengerTypeCode, dateOfBirth, passportDetails
        - Per-passenger pricing in data.air.prices.unitPrices (linked by travelerIds)
        - Baggage allowance in data.air.freeCheckedBaggageAllowanceItems (linked by travelerIds)
        - Contact details at data.contactDetails (applies to all pax / lead)
        - No per-pax meal/seat blocks in this response
        """
        pax_docs   = []
        travelers  = self.data.get("travelers", [])

        # Build price map: travelerId → unit price block
        price_map: dict = {}
        for up in self.air.get("prices", {}).get("unitPrices", []):
            for tid in up.get("travelerIds", []):
                price_map[tid] = up.get("prices", [{}])[0]

        # Build baggage map: travelerId → list of baggage items
        baggage_map: dict = {}
        for bag in self.air.get("freeCheckedBaggageAllowanceItems", []):
            for tid in bag.get("travelerIds", []):
                baggage_map.setdefault(tid, []).append({
                    "segment_ids": bag.get("segmentIds", []),
                    "details":     bag.get("details", {}),
                })

        contact = self.data.get("contactDetails", {})

        for traveler in travelers:
            tid  = traveler.get("id")
            name = traveler.get("name", {})

            each_ci_id = generate_numeric_uuid()
            price      = price_map.get(tid, {})

            pax_docs.append({
                "parent_ci_id": self.ci_id,
                "ci_id":        each_ci_id,
                "airline":      "LotPolish",
                "is_deleted":   False,

                "pnr":       pnr,
                "last_name": last_name,

                "traveler_id":         tid,
                "passenger_type_code": traveler.get("passengerTypeCode"),  # ADT / CHD / INF

                "title":      name.get("title"),
                "first_name": name.get("firstName"),
                "last_name":  name.get("lastName"),

                "date_of_birth": traveler.get("dateOfBirth"),

                # Passport / travel document
                "passport_details": traveler.get("passportDetails", {}),

                # Contact (shared / lead pax)
                "contact_details": {
                    "email":                   contact.get("email"),
                    "phone_number":            contact.get("phoneNumber"),
                    "country_phone_extension": contact.get("countryPhoneExtension"),
                },

                # Per-pax pricing
                "price": {
                    "base":        price.get("base", {}).get("value"),
                    "total":       price.get("total", {}).get("value"),
                    "total_taxes": price.get("totalTaxes", {}).get("value"),
                    "currency":    price.get("total", {}).get("currencyCode"),
                    "taxes":       price.get("taxes", []),
                },

                # Free checked baggage entitlement per segment
                "free_checked_baggage": baggage_map.get(tid, []),

                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })

        return pax_docs

    # =========================================================
    # 4. FLIGHTS  (one doc per segment)
    # =========================================================

    def _build_flight(self, pnr, last_name):
        """
        Collection : flight_info

        LOT-specific notes:
        - Flights live in data.air.flights[]; each flight has segments[]
        - All code → name lookups resolved from dictionaries block
          (location, airline, aircraft)
        - Disruption status attached at flight level (disruptionStatus)
        - connectionTime between segments lives on the segment, not the route
        - fareFamilyCode on both flight and segment level
        - No checkinOpen flag in this response
        """
        flight_docs = []

        seg_dict      = self.dicts.get("segment", {})
        loc_dict      = self.dicts.get("location", {})
        airline_dict  = self.dicts.get("airline", {})
        aircraft_dict = self.dicts.get("aircraft", {})

        for flight in self.air.get("flights", []):
            flight_id        = flight.get("flightId")
            fare_family_code = flight.get("fareFamilyCode")
            flight_type      = flight.get("flightType")        # DIRECT / CONNECTING
            disruption       = flight.get("disruptionStatus")
            flight_duration  = flight.get("duration")          # seconds

            for segment in flight.get("segments", []):
                seg_id   = segment.get("segmentId")
                seg_info = seg_dict.get(seg_id, {})

                dep = segment.get("departure", {})
                arr = segment.get("arrival",   {})

                dep_loc = loc_dict.get(dep.get("locationCode"), {})
                arr_loc = loc_dict.get(arr.get("locationCode"), {})

                each_ci_id = generate_numeric_uuid()

                flight_docs.append({
                    "parent_ci_id": self.ci_id,
                    "ci_id":        each_ci_id,
                    "airline":      "LotPolish",
                    "is_deleted":   False,

                    "pnr":       pnr,
                    "last_name": last_name,

                    # Flight level
                    "flight_id":       flight_id,
                    "flight_type":     flight_type,
                    "fare_family_code": fare_family_code,
                    "flight_duration": flight_duration,

                    "origin":      flight.get("originLocationCode"),
                    "destination": flight.get("destinationLocationCode"),

                    # Segment level
                    "segment_id":      seg_id,
                    "compartment":     segment.get("compartment"),   # ECONOMY / BUSINESS
                    "booking_class":   segment.get("bookingClass"),  # S / L / Y …
                    "status_code":     segment.get("statusCode"),    # HK
                    "connection_time": segment.get("connectionTime"),
                    "gifted_fast_track": segment.get("giftedFastTrack"),
                    "arrival_days_difference": segment.get("arrivalDaysDifference"),

                    "departure": {
                        "airport":      dep.get("locationCode"),
                        "airport_name": dep_loc.get("airportName"),
                        "city":         dep_loc.get("cityName"),
                        "country":      dep_loc.get("countryCode"),
                        "terminal":     dep.get("terminal"),
                        "date_time":    dep.get("dateTime"),
                        "timezone":     dep_loc.get("timeZone"),
                    },
                    "arrival": {
                        "airport":      arr.get("locationCode"),
                        "airport_name": arr_loc.get("airportName"),
                        "city":         arr_loc.get("cityName"),
                        "country":      arr_loc.get("countryCode"),
                        "terminal":     arr.get("terminal"),
                        "date_time":    arr.get("dateTime"),
                        "timezone":     arr_loc.get("timeZone"),
                    },

                    # Airline & aircraft (resolved via dictionaries)
                    "marketing_airline":      seg_info.get("marketingAirlineCode"),
                    "marketing_airline_name": airline_dict.get(seg_info.get("marketingAirlineCode")),
                    "flight_number":          seg_info.get("marketingFlightNumber"),
                    "operating_airline":      seg_info.get("operatingAirlineCode"),
                    "operating_flight_number": seg_info.get("operatingAirlineFlightNumber"),

                    "aircraft_code": seg_info.get("aircraftCode"),
                    "aircraft_name": aircraft_dict.get(seg_info.get("aircraftCode")),

                    "segment_duration":      seg_info.get("duration"),
                    "secure_flight_indicator": seg_info.get("secureFlightIndicator"),
                    "baggage_allowance_ids": seg_info.get("baggageAllowanceIds", []),

                    # Disruption (flight level — only on impacted flights)
                    "disruption_status": disruption,

                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                })

        return flight_docs

    # =========================================================
    # 5. FARE  (one doc per travel document / ticket)
    # =========================================================

    def _build_fare(self, pnr, last_name):
        """
        Collection : fare_info

        LOT-specific notes:
        - Ticket/fare info lives in data.travelDocuments[]
        - Each travelDocument links to travelerIds and segmentIds
        - fareInfos array inside travelDocument holds per-coupon detail
          (fareClass, fareFamilyCode, couponStatus, flight info)
        - Payment method stored in paymentTransactions[]
        - Baggage allowance per coupon in fareInfos[].freeCheckedBaggageAllowanceItems
        - fare families decoded via dictionaries.fareFamily
        - data.air.fareInfos holds the booking-class / fare-class per traveler+segment
        """
        fare_docs    = []
        fare_family  = self.dicts.get("fareFamily", {})

        # Build traveler name map for quick lookup
        pax_map: dict = {
            t["id"]: t for t in self.data.get("travelers", [])
        }

        # Air-level fareInfos: fareClass per travelerIds + segmentIds
        air_fare_map: dict = {}
        for fi in self.air.get("fareInfos", []):
            for tid in fi.get("travelerIds", []):
                air_fare_map.setdefault(tid, []).append({
                    "fare_class":   fi.get("fareClass"),
                    "segment_ids":  fi.get("segmentIds", []),
                })

        for doc in self.data.get("travelDocuments", []):
            doc_price    = doc.get("price", {})
            pax_ids      = doc.get("travelerIds", [])
            each_ci_id   = generate_numeric_uuid()

            # Resolve passenger info (typically one pax per e-ticket)
            pax_id   = pax_ids[0] if pax_ids else None
            pax_info = pax_map.get(pax_id, {})
            pax_name = pax_info.get("name", {})

            # Coupon-level fare breakdown (one entry per flight coupon)
            coupon_breakdowns = []
            for fi in doc.get("fareInfos", []):
                ffc  = fi.get("fareFamilyCode")
                flt  = fi.get("flight", {})
                coupon_breakdowns.append({
                    "fare_class":        fi.get("fareClass"),
                    "fare_family_code":  ffc,
                    "fare_family_title": fare_family.get(ffc, {}).get("title"),
                    "coupon_status":     fi.get("couponStatus"),       # open / used / void
                    "flight_id":         flt.get("id"),                # segment id (ST1 …)
                    "departure": {
                        "airport":   flt.get("departure", {}).get("locationCode"),
                        "date_time": flt.get("departure", {}).get("dateTime"),
                    },
                    "arrival": {
                        "airport": flt.get("arrival", {}).get("locationCode"),
                    },
                    "free_checked_baggage": fi.get("freeCheckedBaggageAllowanceItems", []),
                })

            fare_docs.append({
                "parent_ci_id": self.ci_id,
                "ci_id":        each_ci_id,
                "airline":      "LotPolish",
                "is_deleted":   False,

                "pnr":       pnr,
                "last_name": last_name,

                # Document identifiers
                "document_id":   doc.get("id"),              # e-ticket number
                "document_type": doc.get("documentType"),    # eticket
                "status":        doc.get("status"),          # ISSUED

                # Linked travelers / segments
                "traveler_ids": pax_ids,
                "segment_ids":  doc.get("segmentIds", []),

                # Passenger snapshot
                "passenger_id":   pax_id,
                "title":          pax_name.get("title"),
                "first_name":     pax_name.get("firstName"),
                "last_name_pax":  pax_name.get("lastName"),

                # Pricing
                "pricing": {
                    "base":        doc_price.get("base"),
                    "total":       doc_price.get("total"),
                    "total_taxes": doc_price.get("totalTaxes"),
                    "currency":    doc_price.get("currencyCode"),
                    "taxes":       doc_price.get("taxes", []),
                },

                # Payment
                "payment_transactions": doc.get("paymentTransactions", []),

                # Per-coupon fare breakdown
                "coupon_breakdowns": coupon_breakdowns,

                # Air-level fare class info for this traveler
                "air_fare_infos": air_fare_map.get(pax_id, []),

                # Metadata flags
                "are_coupons_and_segments_in_sync": doc.get("areCouponsAndSegmentsInSync"),
                "eligible_for_invoicing":           doc.get("eligibleForInvoicing"),

                # Issuance provenance
                "creation": doc.get("creation", {}),

                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })

        return fare_docs

    # =========================================================
    # HELPER
    # =========================================================

    def _extract_last_name(self):
        travelers = self.data.get("travelers", [])
        if not travelers:
            return ""
        return travelers[0].get("name", {}).get("lastName", "")