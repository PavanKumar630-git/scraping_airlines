from datetime import datetime
from airlines_main.utility import generate_numeric_uuid
from app.scraping.services.mongo_service import MongoService


class AzalIngestionService:

    def __init__(self, raw_data: dict, ci_id):
        self.raw    = raw_data
        # Azal response root has 'order' not 'data'
        self.order  = raw_data.get("order", raw_data)
        self.flight = self.order.get("flight", {})
        self.ci_id  = str(ci_id)

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
        pnr       = self.flight.get("pnr")
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
            "airline":    "Azal",
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

        Azal-specific differences:
        - Root key is 'order' not 'data'
        - order.id is the booking UUID
        - order.flight.pnr is the PNR
        - Total pricing in order.flight.pricing
        - Refund/reissue availability at order level
        - Meals/bags/seats as separate product blocks
        - banners block at root level
        """
        flight_pricing = self.flight.get("pricing", {})
        total_price    = flight_pricing.get("total", {})
        base_price     = flight_pricing.get("base", {})
        taxes          = flight_pricing.get("taxes", [])

        each_ci_id = generate_numeric_uuid()

        return {
            "parent_ci_id": self.ci_id,
            "ci_id":        each_ci_id,
            "airline":      "Azal",
            "is_deleted":   False,

            "pnr":       pnr,
            "last_name": last_name,

            # Booking metadata
            "order_id":   self.order.get("id"),

            # Total booking price
            "total_price": {
                "total":    total_price.get("price"),
                "base":     base_price.get("price"),
                "taxes":    taxes,
                "currency": total_price.get("price", {}).get("currency"),
            },

            # Refund / reissue availability
            "refund_availability":  self.order.get("refundAvailability", {}),
            "reissue_availability": self.order.get("reissueAvailability", {}),
            "verified_operations":  self.order.get("verifiedOperations", {}),

            # Add-on product summaries
            "meals_products":   self.order.get("meals", {}).get("products", []),
            "bags_products":    self.order.get("bags", {}).get("products", []),
            "seats_products":   self.order.get("seats", {}).get("products", []),

            # Analytic / payment banners
            "payment_banners":    self.flight.get("paymentBanners", []),
            "analytic_parameters": self.flight.get("analyticParameters", {}),

            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

    # =========================================================
    # 3. PASSENGERS  (one doc per passenger)
    # =========================================================

    def _build_pax(self, pnr, last_name):
        """
        Collection : pax_info

        Azal-specific differences:
        - Passengers live in order.flight.passengers
        - Each passenger has: id, name{firstName, lastName}, type, contacts, lead, tickets[]
        - Pricing per passenger in order.flight.passengerBreakdowns (linked by passengerIds)
        - Meals linked by passengerId in order.meals.products
        - Seats linked by passengerId in order.seats.products
        - No regulatoryDetails / passport block in this response
        """
        pax_docs   = []
        passengers = self.flight.get("passengers", [])

        # Build price map: passengerId → pricing + segmentBreakdowns
        price_map: dict = {}
        for pb in self.flight.get("passengerBreakdowns", []):
            for pid in pb.get("passengerIds", []):
                price_map[pid] = {
                    "passenger_type":      pb.get("passengerType"),
                    "pricing":             pb.get("pricing", {}),
                    "segment_breakdowns":  pb.get("segmentBreakdowns", []),
                    "with_promo_code":     pb.get("withPersonalPromoCode"),
                }

        # Build meal map: passengerId → list of meals
        meal_map: dict = {}
        for meal in self.order.get("meals", {}).get("products", []):
            pid = meal.get("passengerId")
            if pid:
                meal_map.setdefault(pid, []).append({
                    "meal_id":    meal.get("id"),
                    "code":       meal.get("code"),       # "VGML"
                    "subcode":    meal.get("subcode"),
                    "segment_id": meal.get("segmentId"),
                    "status":     meal.get("status"),
                    "details":    meal.get("details", {}),
                    "pricing":    meal.get("pricing", {}),
                })

        # Build seat map: passengerId → list of seats
        seat_map: dict = {}
        for seat in self.order.get("seats", {}).get("products", []):
            pid = seat.get("passengerId")
            if pid:
                seat_map.setdefault(pid, []).append(seat)

        for pax in passengers:
            pid  = pax.get("id")
            name = pax.get("name", {})

            each_ci_id = generate_numeric_uuid()

            pax_docs.append({
                "parent_ci_id": self.ci_id,
                "ci_id":        each_ci_id,
                "airline":      "Azal",
                "is_deleted":   False,

                "pnr":       pnr,
                "last_name": last_name,

                "passenger_id":          pid,
                "passenger_type_code":   pax.get("type"),          # ADT / CHD / INF
                "is_lead":               pax.get("lead", False),

                "first_name": name.get("firstName"),
                "last_name":  name.get("lastName"),

                # Contact (only lead pax usually has this)
                "contacts": pax.get("contacts", {}),

                # Ticket numbers linked to this pax
                "tickets": pax.get("tickets", []),    # [{number, status}]

                # Per-passenger pricing + fare breakdown per segment
                "price": price_map.get(pid),

                # Meals booked for this pax
                "meals": meal_map.get(pid, []),

                # Seats booked for this pax
                "seats": seat_map.get(pid, []),

                # Flags
                "special_assistance_available": pax.get("specialAssistanceAvailable"),
                "document_edit_disabled":        pax.get("documentEditDisabled"),
                "document_required":             pax.get("documentRequired"),

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

        Azal-specific differences:
        - Flights live in order.flight.routes[].segments[]
        - Route has: departure, arrival, departureDate, arrivalDate, duration, stops
        - Segment has: departureAirport{code,terminal}, arrivalAirport, operatingAirline, marketingAirline, aircraft
        - No dictionaries block — all info inline in segment
        - reissueAvailability per route and per passengerId
        - checkinOpen flag on segment
        """
        flights = []
        routes  = self.flight.get("routes", [])

        for route in routes:
            route_id = route.get("id")

            for segment in route.get("segments", []):
                segment_id = segment.get("id")

                each_ci_id = generate_numeric_uuid()

                flights.append({
                    "parent_ci_id": self.ci_id,
                    "ci_id":        each_ci_id,
                    "airline":      "Azal",
                    "is_deleted":   False,

                    "pnr":       pnr,
                    "last_name": last_name,

                    # Route level
                    "route_id":    route_id,
                    "origin":      route.get("departure"),
                    "destination": route.get("arrival"),
                    "route_duration": route.get("duration"),   # {days, hours, minutes}
                    "stops":       route.get("stops", []),

                    # Segment level
                    "segment_id": segment_id,

                    "departure": {
                        "airport":   segment.get("departureAirport", {}).get("code"),
                        "terminal":  segment.get("departureAirport", {}).get("terminal"),
                        "date_time": segment.get("departureDate"),
                        "timezone":  segment.get("departureTimeZone"),
                    },
                    "arrival": {
                        "airport":   segment.get("arrivalAirport", {}).get("code"),
                        "terminal":  segment.get("arrivalAirport", {}).get("terminal"),
                        "date_time": segment.get("arrivalDate"),
                        "timezone":  segment.get("arrivalTimeZone"),
                    },

                    "segment_duration": segment.get("duration"),

                    # Airline info (inline, no dictionaries block)
                    "marketing_airline": segment.get("marketingAirline", {}).get("code"),
                    "flight_number":     segment.get("marketingAirline", {}).get("flightNumber"),
                    "operating_airline": segment.get("operatingAirline", {}).get("code"),
                    "operating_flight_number": segment.get("operatingAirline", {}).get("flightNumber"),

                    # Aircraft
                    "aircraft_code": segment.get("aircraft", {}).get("code"),
                    "aircraft_name": segment.get("aircraft", {}).get("name"),

                    # Flags
                    "checkin_open": segment.get("checkinOpen"),

                    # Reissue availability per route
                    "reissue_availability":              route.get("reissueAvailability", {}),
                    "reissue_availability_by_passenger": route.get("reissueAvailabilityByPassengerId", {}),

                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                })

        return flights

    # =========================================================
    # 5. FARE  (one doc per passenger — ticket + fare breakdown)
    # =========================================================

    def _build_fare(self, pnr, last_name):
        """
        Collection : fare_info

        Azal-specific differences:
        - No travelDocuments block — ticket number is inside passengers[].tickets[]
        - Fare details (fareFamily, cabin, rbd, fareCode, facilities) are in
          passengerBreakdowns[].segmentBreakdowns[].fare
        - One fare doc per passenger (linked by passengerIds)
        - Pricing: base, total, taxes at passengerBreakdown level
        """
        fares      = []
        passengers = self.flight.get("passengers", [])

        # Map passengerId → passenger info for name/ticket lookup
        pax_map: dict = {p["id"]: p for p in passengers}

        for pb in self.flight.get("passengerBreakdowns", []):
            pricing    = pb.get("pricing", {})
            seg_breaks = pb.get("segmentBreakdowns", [])

            # Flatten per-segment fare info
            fare_breakdowns = []
            for sb in seg_breaks:
                fare = sb.get("fare", {})
                fare_breakdowns.append({
                    "segment_id":    sb.get("segmentId"),
                    "fare_family":   fare.get("fareFamily"),   # "CLASSIC"
                    "cabin":         fare.get("cabin"),         # "ECONOMY"
                    "rbd":           fare.get("rbd"),           # "U"
                    "fare_code":     fare.get("fareCode"),      # "UK0R23CL"
                    "facilities":    fare.get("facilities", []), # baggage/meal info
                })

            for pid in pb.get("passengerIds", []):
                pax      = pax_map.get(pid, {})
                tickets  = pax.get("tickets", [])
                each_ci_id = generate_numeric_uuid()

                fares.append({
                    "parent_ci_id": self.ci_id,
                    "ci_id":        each_ci_id,
                    "airline":      "Azal",
                    "is_deleted":   False,

                    "pnr":       pnr,
                    "last_name": last_name,

                    "passenger_id":   pid,
                    "passenger_type": pb.get("passengerType"),   # ADT / CHD

                    # Ticket info from passenger block
                    "ticket_number": tickets[0].get("number") if tickets else None,
                    "ticket_status": tickets[0].get("status") if tickets else None,
                    "all_tickets":   tickets,

                    # Per-passenger pricing
                    "pricing": {
                        "total":    pricing.get("total", {}).get("price"),
                        "base":     pricing.get("base", {}).get("price"),
                        "taxes":    pricing.get("taxes", []),
                        "currency": pricing.get("total", {}).get("price", {}).get("currency"),
                    },

                    # Fare breakdown per segment
                    "fare_breakdowns": fare_breakdowns,

                    "with_promo_code": pb.get("withPersonalPromoCode", False),

                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                })

        return fares

    # =========================================================
    # HELPER
    # =========================================================

    def _extract_last_name(self):
        passengers = self.flight.get("passengers", [])
        if not passengers:
            return ""
        return passengers[0].get("name", {}).get("lastName", "")