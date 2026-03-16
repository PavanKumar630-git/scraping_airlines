from datetime import datetime
from airlines_main.utility import generate_numeric_uuid
from app.scraping.services.mongo_service import MongoService


class MalaysiaIngestionService:

    def __init__(self, raw_data: dict, ci_id):
        self.raw  = raw_data
        self.data = raw_data.get("data", raw_data)
        self.ci_id = str(ci_id)

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
        pnr       = self.data.get("id")
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
        Stores the complete unmodified API response for audit / replay.
        """
        self.raw_col.insert_one({
            "ci_id":      self.ci_id,
            "airline":    "Malaysia",
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
        Top-level booking metadata, ticket summary, pricing totals,
        contacts, eligibilities.

        Malaysia-specific differences vs SriLankan:
        - Multiple travelDocuments (one per traveler)
        - air.prices block with unitPrices + totalPrices
        - fareElements (FT remarks)
        - id field is at the bottom of data dict
        """
        travel_docs = self.data.get("travelDocuments", [])
        ticket      = travel_docs[0] if travel_docs else {}

        creation_info   = ticket.get("creation", {})
        issuance_office = creation_info.get("office", {}).get("officeId")
        issuance_city   = creation_info.get("location", {}).get("cityCode")
        issuance_date   = creation_info.get("localDateTime")

        # Total price across all travelers
        air           = self.data.get("air", {})
        prices        = air.get("prices", {})
        total_prices  = prices.get("totalPrices", [{}])
        total_price   = total_prices[0] if total_prices else {}

        each_ci_id = generate_numeric_uuid()

        return {
            "parent_ci_id": self.ci_id,
            "ci_id":        each_ci_id,
            "airline":      "Malaysia",
            "is_deleted":   False,

            "pnr":       pnr,
            "last_name": last_name,

            # Booking metadata
            "order_id":                   self.data.get("id"),
            "creation_datetime":          self.data.get("creationDateTime"),
            "last_modification_datetime": self.data.get("lastModificationDateTime"),
            "is_group_booking":           self.data.get("isGroupBooking", False),

            # Points of sale
            "creation_pos":  self.data.get("creationPointOfSale"),
            "servicing_pos": self.data.get("servicingPointOfSale"),

            # First ticket summary
            "ticket_number": ticket.get("id"),
            "document_type": ticket.get("documentType"),
            "status":        ticket.get("status"),
            "endorsement":   ticket.get("endorsement"),  # "NONEND-SUBJ TO PENALTY"

            # Issuance info
            "issuance_office": issuance_office,
            "issuance_city":   issuance_city,
            "issuance_date":   issuance_date,

            # Total booking price (Malaysia has full pricing unlike SriLankan)
            "total_price": {
                "base":        total_price.get("base"),
                "total":       total_price.get("total"),
                "total_taxes": total_price.get("totalTaxes"),
                "currency":    total_price.get("base", {}).get("currencyCode") if isinstance(total_price.get("base"), dict) else None,
            },

            # Contacts
            "contacts": self.data.get("contacts", []),

            # Malaysia-specific: FT fare remark elements
            "fare_elements": self.data.get("fareElements", []),

            # SSRs, eligibilities
            "special_service_requests": self.data.get("specialServiceRequests", []),
            "remarks":                  self.data.get("remarks", []),
            "warnings":                 self.raw.get("warnings", []),
            "order_eligibilities":      self.data.get("orderEligibilities"),

            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

    # =========================================================
    # 3. PASSENGERS  (one doc per traveler)
    # =========================================================

    def _build_pax(self, pnr, last_name):
        """
        Collection : pax_info
        One document per traveler.

        Malaysia-specific differences vs SriLankan:
        - No seats block in this booking
        - No services block (only CHLD SSR for child)
        - Has dateOfBirth for child passenger (PT3)
        - Multiple ADT + CHD pax types
        - Per-traveler unit prices from air.prices.unitPrices
        """
        pax_docs    = []
        travelers   = self.data.get("travelers", [])
        seats       = self.data.get("seats", [])
        services    = self.data.get("services", [])

        # Build per-traveler price map from air.prices.unitPrices
        air         = self.data.get("air", {})
        unit_prices = air.get("prices", {}).get("unitPrices", [])
        price_map: dict = {}
        for up in unit_prices:
            price_data = up.get("prices", [{}])[0] if up.get("prices") else {}
            for tid in up.get("travelerIds", []):
                price_map[tid] = {
                    "base":        price_data.get("base"),
                    "total":       price_data.get("total"),
                    "total_taxes": price_data.get("totalTaxes"),
                    "taxes":       price_data.get("taxes", []),
                    "flight_ids":  up.get("flightIds", []),
                }

        # Build per-traveler SSR map
        ssrs     = self.data.get("specialServiceRequests", [])
        ssr_map: dict = {}
        for ssr in ssrs:
            for tid in ssr.get("travelerIds", []):
                ssr_map.setdefault(tid, []).append(ssr)

        for traveler in travelers:
            name        = traveler.get("names", [{}])[0]
            traveler_id = traveler.get("id")

            # Seats (empty in this PNR but kept for future)
            mapped_seats = []
            for seat in seats:
                for sel in seat.get("seatSelections", []):
                    if sel.get("travelerId") == traveler_id:
                        mapped_seats.append({
                            "seat_id":         seat.get("id"),
                            "flight_id":       seat.get("flightId"),
                            "seat_number":     sel.get("seatNumber"),
                            "characteristics": sel.get("seatCharacteristics", []),
                            "is_chargeable":   sel.get("isChargeable"),
                            "status_code":     seat.get("statusCode"),
                        })

            # Services
            mapped_services = []
            for svc in services:
                svc_traveler_ids = svc.get("travelerIds") or []
                if not svc_traveler_ids or traveler_id in svc_traveler_ids:
                    mapped_services.append(svc)

            each_ci_id = generate_numeric_uuid()

            pax_docs.append({
                "parent_ci_id": self.ci_id,
                "ci_id":        each_ci_id,
                "airline":      "Malaysia",
                "is_deleted":   False,

                "pnr":       pnr,
                "last_name": last_name,

                "traveler_id":         traveler_id,
                "passenger_type_code": traveler.get("passengerTypeCode"),  # ADT / CHD

                "first_name":    name.get("firstName"),
                "last_name":     name.get("lastName"),
                "title":         name.get("title"),

                # Malaysia-specific: child DOB
                "date_of_birth": traveler.get("dateOfBirth"),

                "regulatory_details": traveler.get("regulatoryDetails", []),

                # Per-traveler price breakdown
                "price": price_map.get(traveler_id),

                # SSRs linked to this traveler (e.g. CHLD for PT3)
                "special_service_requests": ssr_map.get(traveler_id, []),

                "seats":    mapped_seats,
                "services": mapped_services,

                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })

        return pax_docs

    # =========================================================
    # 4. FLIGHTS  (one doc per segment / flight leg)
    # =========================================================

    def _build_flight(self, pnr, last_name):
        """
        Collection : flight_info
        One document per flight segment enriched from dictionaries.

        Malaysia-specific differences vs SriLankan:
        - fareFamilyCode on both bound and segment level (BASIC)
        - commercialFareFamilyCode on segment level (CFFMH)
        - connectionTime on some segments
        - arrivalDaysDifference on overnight flights
        - baggage per traveler group (PT1+PT2 vs PT3 separate entries)
        """
        flights     = []
        air         = self.data.get("air", {})
        bounds      = air.get("bounds", [])
        flight_dict = self.data.get("dictionaries", {}).get("flight", {})

        # Baggage map: segment_id → list of {travelerIds, details}
        baggage_items = air.get("freeCheckedBaggageAllowanceItems", [])
        baggage_map: dict = {}
        for bi in baggage_items:
            for fid in bi.get("flightIds", []):
                baggage_map.setdefault(fid, []).append({
                    "traveler_ids": bi.get("travelerIds", []),
                    "details":      bi.get("details", {}),
                })

        for bound in bounds:
            for fl in bound.get("flights", []):
                segment_id  = fl.get("id")
                flight_info = flight_dict.get(segment_id, {})

                each_ci_id = generate_numeric_uuid()

                flights.append({
                    "parent_ci_id": self.ci_id,
                    "ci_id":        each_ci_id,
                    "airline":      "Malaysia",
                    "is_deleted":   False,

                    "pnr":       pnr,
                    "last_name": last_name,

                    # Bound level
                    "air_bound_id":    bound.get("airBoundId"),
                    "origin":          bound.get("originLocationCode"),
                    "destination":     bound.get("destinationLocationCode"),
                    "duration":        bound.get("duration"),          # seconds
                    "fare_family_code": bound.get("fareFamilyCode"),   # "BASIC"

                    # Segment level
                    "segment_id":               segment_id,
                    "cabin":                    fl.get("cabin"),
                    "booking_class":            fl.get("bookingClass"),
                    "status_code":              fl.get("statusCode"),
                    "fare_family_code_segment": fl.get("fareFamilyCode"),
                    "commercial_fare_family":   fl.get("commercialFareFamilyCode"),  # "CFFMH"
                    "connection_time":          fl.get("connectionTime"),             # seconds
                    "arrival_days_difference":  fl.get("arrivalDaysDifference"),     # overnight flag

                    # Enriched from dictionaries.flight
                    "marketing_airline":         flight_info.get("marketingAirlineCode"),
                    "operating_airline":         flight_info.get("operatingAirlineCode"),
                    "flight_number":             flight_info.get("marketingFlightNumber"),
                    "operating_flight_number":   flight_info.get("operatingAirlineFlightNumber"),

                    "departure": flight_info.get("departure"),   # {locationCode, dateTime, terminal}
                    "arrival":   flight_info.get("arrival"),     # {locationCode, dateTime, terminal}

                    "aircraft_code":  flight_info.get("aircraftCode"),
                    "flight_status":  flight_info.get("flightStatus"),
                    "meals":          flight_info.get("meals"),

                    # Baggage per traveler group for this segment
                    "free_checked_baggage": baggage_map.get(segment_id, []),

                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                })

        return flights

    # =========================================================
    # 5. FARE  (one doc per e-ticket / travel document)
    # =========================================================

    def _build_fare(self, pnr, last_name):
        """
        Collection : fare_info
        One document per e-ticket (Malaysia has 3 tickets: PT1, PT2, PT3).

        Malaysia-specific differences vs SriLankan:
        - Full price block with taxes, totalTaxes, priceBreakdowns
        - fareFamilyCode on each coupon
        - ticketDesignator (PVT) on fareInfos
        - payment amount specified per transaction
        """
        fares       = []
        travel_docs = self.data.get("travelDocuments", [])

        for doc in travel_docs:
            price      = doc.get("price", {})
            fare_infos = doc.get("fareInfos", [])

            # Flatten coupon data
            coupons = []
            for fi in fare_infos:
                coupons.append({
                    "fare_info_id":     fi.get("id"),
                    "fare_class":       fi.get("fareClass"),       # "NBX1YIZ/PVT"
                    "fare_family_code": fi.get("fareFamilyCode"),  # "BASIC"
                    "coupon_status":    fi.get("couponStatus"),
                    "flight_id":        fi.get("flight", {}).get("id"),
                    "flight_number":    fi.get("flight", {}).get("marketingFlightNumber"),
                    "airline_code":     fi.get("flight", {}).get("marketingAirlineCode"),
                    "departure":        fi.get("flight", {}).get("departure"),
                    "arrival":          fi.get("flight", {}).get("arrival"),
                    "free_baggage":     fi.get("freeCheckedBaggageAllowanceItems", []),
                })

            each_ci_id = generate_numeric_uuid()

            fares.append({
                "parent_ci_id": self.ci_id,
                "ci_id":        each_ci_id,
                "airline":      "Malaysia",
                "is_deleted":   False,

                "pnr":       pnr,
                "last_name": last_name,

                "ticket_number": doc.get("id"),
                "document_type": doc.get("documentType"),
                "status":        doc.get("status"),
                "endorsement":   doc.get("endorsement"),  # "NONEND-SUBJ TO PENALTY"

                "traveler_ids": doc.get("travelerIds", []),
                "flight_ids":   doc.get("flightIds", []),

                "coupons_in_sync": doc.get("areCouponsAndSegmentsInSync"),

                # Coupon / fare breakdowns
                "fare_breakdowns": coupons,

                # Full price block (Malaysia always has this populated)
                "pricing": {
                    "base":        price.get("base"),
                    "total":       price.get("total"),
                    "total_taxes": price.get("totalTaxes"),
                    "currency":    price.get("currencyCode"),
                    "taxes":       price.get("taxes", []),
                },
                "price_breakdowns": price.get("priceBreakdowns", []),

                # Payment
                "payment_transactions": doc.get("paymentTransactions", []),

                # Issuance audit trail
                "creation": doc.get("creation", {}),

                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })

        return fares

    # =========================================================
    # HELPER
    # =========================================================

    def _extract_last_name(self):
        travelers = self.data.get("travelers", [])
        if not travelers:
            return ""
        names = travelers[0].get("names", [])
        if not names:
            return ""
        return names[0].get("lastName", "")