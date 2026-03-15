
from django.db import models

class AirIndiaDocument(models.Model):
    
    pdf_url = models.URLField()
    file_path = models.CharField(max_length=500)
    source = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

class UsersModel(models.Model):
    websitename = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)




# booking/models.py
"""
MongoEngine document models for flight booking data.
4 collections: HeaderInfo, PaxInfo, FlightInfo, FareInfo
All linked by ci_id (UUID), pnr, and last_name.
"""

import uuid
from mongoengine import (
    Document, EmbeddedDocument, StringField, DateTimeField,
    BooleanField, IntField, ListField,
    EmbeddedDocumentField, EmbeddedDocumentListField,
    UUIDField,
)


# ════════════════════════════════════════════════════════════
# SHARED EMBEDDED DOCUMENTS
# ════════════════════════════════════════════════════════════

class PointOfSale(EmbeddedDocument):
    point_of_sale_id = StringField()
    country_code     = StringField(max_length=5)


class LocationDateTime(EmbeddedDocument):
    location_code = StringField(max_length=10)
    date_time     = DateTimeField()
    terminal      = StringField()


class MoneyAmount(EmbeddedDocument):
    value         = IntField()
    currency_code = StringField(max_length=5, default="INR")


class TaxItem(EmbeddedDocument):
    code          = StringField(max_length=20)
    description   = StringField()
    value         = IntField()
    currency_code = StringField(max_length=5, default="INR")


class SurchargeItem(EmbeddedDocument):
    code          = StringField(max_length=20)
    description   = StringField()
    value         = IntField()
    currency_code = StringField(max_length=5, default="INR")


# ════════════════════════════════════════════════════════════
# 1. HEADER INFO COLLECTION
# ════════════════════════════════════════════════════════════

class ContactItem(EmbeddedDocument):
    contact_id              = StringField()       # renamed from 'id' to avoid shadowing built-in
    category                = StringField()
    contact_type            = StringField()       # Phone | Email
    device_type             = StringField()       # mobile | landline
    purpose                 = StringField()       # standard | notification
    number                  = StringField()
    address                 = StringField()       # for email
    country_phone_extension = StringField()
    free_flow_text          = StringField()


class RemarkItem(EmbeddedDocument):
    remark_id   = StringField()                   # renamed from 'id'
    remark_type = StringField()
    freetext    = StringField()
    flight_ids  = ListField(StringField())


class DisruptionWarning(EmbeddedDocument):
    code  = StringField()
    title = StringField()


class EligibilityReason(EmbeddedDocument):
    code  = StringField()
    title = StringField()


class EligibilityStatus(EmbeddedDocument):
    is_eligible             = BooleanField(default=False)
    non_eligibility_reasons = EmbeddedDocumentListField(EligibilityReason)


class PaymentRecord(EmbeddedDocument):
    method         = StringField()
    payment_type   = StringField()
    total_amount   = IntField()
    currency_code  = StringField(default="INR")
    transaction_id = StringField()


class OrderEligibilities(EmbeddedDocument):
    cancel_and_refund = EmbeddedDocumentField(EligibilityStatus)
    change            = EmbeddedDocumentField(EligibilityStatus)
    seat_change       = EmbeddedDocumentField(EligibilityStatus)
    service_change    = EmbeddedDocumentField(EligibilityStatus)
    name_modification = EmbeddedDocumentField(EligibilityStatus)
    passenger_change  = EmbeddedDocumentField(EligibilityStatus)


class HeaderInfo(Document):
    """Top-level booking/order metadata."""

    # ── Cross-collection keys ─────────────────────────────
    ci_id     = UUIDField(primary_key=False, default=uuid.uuid4, unique=False)
    pnr       = StringField(required=True, max_length=20)
    last_name = StringField(required=True, max_length=100)

    # ── Order details ─────────────────────────────────────
    order_id                    = StringField(required=True)
    creation_date_time          = DateTimeField()
    last_modification_date_time = DateTimeField()
    is_group_booking            = BooleanField(default=False)

    creation_pos  = EmbeddedDocumentField(PointOfSale)
    servicing_pos = EmbeddedDocumentField(PointOfSale)

    # ── Ticket ────────────────────────────────────────────
    ticket_number = StringField()
    document_type = StringField(default="eticket")
    ticket_status = StringField()             # ISSUED | REFUNDED | VOID
    endorsement   = StringField()
    tour_code     = StringField()

    # ── Issuance ──────────────────────────────────────────
    issuance_office = StringField()
    issuance_city   = StringField()
    issuance_date   = DateTimeField()

    # ── Payment ───────────────────────────────────────────
    payment = EmbeddedDocumentField(PaymentRecord)

    # ── Contacts / Remarks ────────────────────────────────
    contacts = EmbeddedDocumentListField(ContactItem)
    remarks  = EmbeddedDocumentListField(RemarkItem)

    # ── Disruption ────────────────────────────────────────
    disruption_warning = EmbeddedDocumentField(DisruptionWarning)
    has_disruption     = BooleanField(default=False)

    # ── Order eligibilities ───────────────────────────────
    order_eligibilities = EmbeddedDocumentField(OrderEligibilities)

    # ── Audit ─────────────────────────────────────────────
    created_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {
        "collection": "HeaderInfo",
        "indexes": [
            "pnr",
            "ci_id",
            "last_name",
            ("pnr", "last_name"),
        ],
    }

    def __str__(self):
        return f"HeaderInfo | PNR: {self.pnr} | ci_id: {self.ci_id}"


# ════════════════════════════════════════════════════════════
# 2. PAX INFO COLLECTION
# ════════════════════════════════════════════════════════════

class PassengerName(EmbeddedDocument):
    first_name   = StringField()
    last_name    = StringField()
    title        = StringField()
    name_type    = StringField()
    is_preferred = BooleanField(default=True)


class PassportDocument(EmbeddedDocument):
    document_type         = StringField()
    number                = StringField()
    expiry_date           = DateTimeField()
    issuance_country_code = StringField(max_length=5)
    nationality_code      = StringField(max_length=5)
    gender                = StringField()
    birth_date            = DateTimeField()
    first_name            = StringField()
    last_name             = StringField()


class SeatCharacteristic(EmbeddedDocument):
    code = StringField()
    name = StringField()


class SeatAssignment(EmbeddedDocument):
    seat_id         = StringField()              # renamed from 'id'
    flight_id       = StringField()
    seat_number     = StringField()
    characteristics = EmbeddedDocumentListField(SeatCharacteristic)
    is_chargeable   = BooleanField(default=False)
    status_code     = StringField()


class MealService(EmbeddedDocument):
    meal_id       = StringField()                # renamed from 'id'
    flight_id     = StringField()
    meal_code     = StringField()                # AVML | VGML | HNML etc.
    meal_name     = StringField()
    quantity      = IntField(default=1)
    is_chargeable = BooleanField(default=False)
    status_code   = StringField()


class SpecialServiceRequest(EmbeddedDocument):
    ssr_id       = StringField()                 # renamed from 'id'
    code         = StringField()                 # AVML | CTCM | DOCS | RQST | OTHS
    name         = StringField()
    airline_code = StringField()
    status_code  = StringField()
    quantity     = IntField(default=1)
    freetext     = StringField()
    flight_ids   = ListField(StringField())
    traveler_ids = ListField(StringField())


class PaxInfo(Document):
    """Passenger profile, passport, SSRs, and seat assignments."""

    # ── Cross-collection keys ─────────────────────────────
    ci_id     = UUIDField(default=uuid.uuid4)
    pnr       = StringField(required=True, max_length=20)
    last_name = StringField(required=True, max_length=100)

    # ── Traveler identity ─────────────────────────────────
    traveler_id         = StringField()          # PT1, PT2 ...
    passenger_type_code = StringField()          # ADT | CHD | INF

    name     = EmbeddedDocumentField(PassengerName)
    passport = EmbeddedDocumentField(PassportDocument)

    # ── In-flight services ────────────────────────────────
    seats         = EmbeddedDocumentListField(SeatAssignment)
    meal_services = EmbeddedDocumentListField(MealService)
    ssrs          = EmbeddedDocumentListField(SpecialServiceRequest)

    # ── Audit ─────────────────────────────────────────────
    created_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {
        "collection": "PaxInfo",
        "indexes": [
            "pnr",
            "ci_id",
            "last_name",
            ("pnr", "last_name"),
            "traveler_id",
        ],
    }

    def __str__(self):
        return f"PaxInfo | {self.name.first_name if self.name else ''} {self.last_name} | PNR: {self.pnr}"


# ════════════════════════════════════════════════════════════
# 3. FLIGHT INFO COLLECTION
# ════════════════════════════════════════════════════════════

class FlightStop(EmbeddedDocument):
    location_code       = StringField()
    airport_name        = StringField()
    city                = StringField()
    arrival_date_time   = DateTimeField()
    departure_date_time = DateTimeField()
    stop_duration       = IntField()             # seconds
    is_change_of_gauge  = BooleanField(default=False)


class DisruptionLocationDetail(EmbeddedDocument):
    location_code = StringField()
    same_airport  = BooleanField()
    same_city     = BooleanField()
    same_day      = BooleanField()
    delta_time    = IntField(default=0)          # seconds


class DisruptionConnectionDetail(EmbeddedDocument):
    status         = StringField()
    same_via_point = BooleanField()
    delta          = IntField(default=0)
    delta_time     = IntField(default=0)


class DisruptionStatus(EmbeddedDocument):
    bound_status               = StringField()   # disrupted | ok
    is_in_check_in_time_window = BooleanField(default=False)
    departure                  = EmbeddedDocumentField(DisruptionLocationDetail)
    arrival                    = EmbeddedDocumentField(DisruptionLocationDetail)
    connection                 = EmbeddedDocumentField(DisruptionConnectionDetail)
    revised_duration           = IntField()      # seconds
    original_flight_ids        = ListField(StringField())


class FlightSegment(EmbeddedDocument):
    flight_id                   = StringField()
    marketing_airline_code      = StringField()
    airline_name                = StringField()
    marketing_flight_number     = StringField()
    operating_flight_number     = StringField()
    cabin                       = StringField()  # business | economy | first
    booking_class               = StringField()
    status_code                 = StringField()  # HK | TK | WL ...
    status_name                 = StringField()
    fare_family_code            = StringField()
    commercial_fare_family_code = StringField()
    aircraft_code               = StringField()
    aircraft_name               = StringField()
    flight_status               = StringField()  # scheduled | cancelled | ...

    departure          = EmbeddedDocumentField(LocationDateTime)
    arrival            = EmbeddedDocumentField(LocationDateTime)
    original_departure = EmbeddedDocumentField(LocationDateTime)  # populated on time-change (TK)

    duration                = IntField()         # seconds
    arrival_days_difference = IntField(default=0)
    stops                   = EmbeddedDocumentListField(FlightStop)
    is_disrupted            = BooleanField(default=False)


class BaggageAllowance(EmbeddedDocument):
    flight_id   = StringField()
    traveler_id = StringField()
    type        = StringField()                  # piece | weight
    quantity    = IntField()
    weight_kg   = IntField()                     # populated when type == weight


class AirBound(EmbeddedDocument):
    air_bound_id              = StringField()
    fare_family_code          = StringField()
    origin_location_code      = StringField()
    origin_airport_name       = StringField()
    origin_city               = StringField()
    destination_location_code = StringField()
    destination_airport_name  = StringField()
    destination_city          = StringField()
    duration                  = IntField()
    is_disrupted              = BooleanField(default=False)
    disruption_status         = EmbeddedDocumentField(DisruptionStatus)
    flights                   = EmbeddedDocumentListField(FlightSegment)


class FlightInfo(Document):
    """All flight bounds, segments, disruption info, and baggage."""

    # ── Cross-collection keys ─────────────────────────────
    ci_id     = UUIDField(default=uuid.uuid4)
    pnr       = StringField(required=True, max_length=20)
    last_name = StringField(required=True, max_length=100)

    bounds             = EmbeddedDocumentListField(AirBound)
    baggage_allowances = EmbeddedDocumentListField(BaggageAllowance)

    # ── Audit ─────────────────────────────────────────────
    created_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {
        "collection": "FlightInfo",
        "indexes": [
            "pnr",
            "ci_id",
            "last_name",
            ("pnr", "last_name"),
        ],
    }

    def __str__(self):
        return f"FlightInfo | PNR: {self.pnr} | Bounds: {len(self.bounds)}"


# ════════════════════════════════════════════════════════════
# 4. FARE INFO COLLECTION
# ════════════════════════════════════════════════════════════

class PricingDetails(EmbeddedDocument):
    base_fare_inr        = IntField()
    total_taxes_inr      = IntField()
    total_surcharges_inr = IntField()
    grand_total_inr      = IntField()
    currency_code        = StringField(default="INR")
    taxes                = EmbeddedDocumentListField(TaxItem)
    surcharges           = EmbeddedDocumentListField(SurchargeItem)
    payment_method       = StringField()
    payment_type         = StringField()
    tour_code            = StringField()


class FareBreakdown(EmbeddedDocument):
    fare_info_id     = StringField()
    flight_id        = StringField()
    fare_class       = StringField()
    fare_family_code = StringField()
    booking_class    = StringField()
    coupon_status    = StringField()             # open | used | void | refunded
    base_fare_nuc    = StringField()
    price_qualifier  = StringField()
    baggage_type     = StringField()
    baggage_quantity = IntField()

    flight_airline      = StringField()
    flight_number       = StringField()
    departure_location  = StringField()
    departure_date_time = DateTimeField()
    arrival_location    = StringField()
    arrival_date_time   = DateTimeField()


class FareElement(EmbeddedDocument):
    element_id   = StringField()                 # renamed from 'id'
    code         = StringField()
    text         = StringField()
    flight_ids   = ListField(StringField())
    traveler_ids = ListField(StringField())


class FareInfo(Document):
    """Pricing, fare classes, taxes, surcharges, and coupon status."""

    # ── Cross-collection keys ─────────────────────────────
    ci_id     = UUIDField(default=uuid.uuid4)
    pnr       = StringField(required=True, max_length=20)
    last_name = StringField(required=True, max_length=100)

    ticket_number  = StringField()
    traveler_id    = StringField()

    pricing         = EmbeddedDocumentField(PricingDetails)
    fare_breakdowns = EmbeddedDocumentListField(FareBreakdown)
    fare_elements   = EmbeddedDocumentListField(FareElement)

    # ── Audit ─────────────────────────────────────────────
    created_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {
        "collection": "FareInfo",
        "indexes": [
            "pnr",
            "ci_id",
            "last_name",
            ("pnr", "last_name"),
            "ticket_number",
        ],
    }

    def __str__(self):
        total = self.pricing.grand_total_inr if self.pricing else "N/A"
        return f"FareInfo | PNR: {self.pnr} | Ticket: {self.ticket_number} | Total: {total}"
