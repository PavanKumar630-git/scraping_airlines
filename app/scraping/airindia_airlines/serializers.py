
from rest_framework import serializers
from .models import AirIndiaDocument

class AirIndiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirIndiaDocument
        fields = "__all__"

class AirIndiaTokenDetails(serializers.Serializer):
    pnr = serializers.CharField()
    last_name = serializers.CharField()

# booking/serializers.py
"""
DRF serializers — plain Serializer classes only.
No ModelSerializer: MongoEngine documents are not Django ORM models.
"""

from rest_framework import serializers


# ── Request serializer (used by the view) ────────────────────

class AirIndiaTokenDetails(serializers.Serializer):
    pnr       = serializers.CharField()
    last_name = serializers.CharField()

class AirIndiaDeleteDetails(serializers.Serializer):
    pnr       = serializers.CharField()
    ci_id = serializers.CharField()

# ════════════════════════════════════════════════════════════
# SHARED
# ════════════════════════════════════════════════════════════

class PointOfSaleSerializer(serializers.Serializer):
    point_of_sale_id = serializers.CharField(allow_null=True)
    country_code     = serializers.CharField(allow_null=True)


class TaxItemSerializer(serializers.Serializer):
    code          = serializers.CharField()
    description   = serializers.CharField(allow_null=True, required=False)
    value         = serializers.IntegerField()
    currency_code = serializers.CharField()


class SurchargeItemSerializer(serializers.Serializer):
    code          = serializers.CharField()
    description   = serializers.CharField(allow_null=True, required=False)
    value         = serializers.IntegerField()
    currency_code = serializers.CharField()


# ════════════════════════════════════════════════════════════
# HEADER INFO
# ════════════════════════════════════════════════════════════

class ContactItemSerializer(serializers.Serializer):
    contact_id              = serializers.CharField(allow_null=True, required=False)
    category                = serializers.CharField(allow_null=True, required=False)
    contact_type            = serializers.CharField(allow_null=True, required=False)
    device_type             = serializers.CharField(allow_null=True, required=False)
    purpose                 = serializers.CharField(allow_null=True, required=False)
    number                  = serializers.CharField(allow_null=True, required=False)
    address                 = serializers.CharField(allow_null=True, required=False)
    country_phone_extension = serializers.CharField(allow_null=True, required=False)
    free_flow_text          = serializers.CharField(allow_null=True, required=False)


class RemarkItemSerializer(serializers.Serializer):
    remark_id   = serializers.CharField(allow_null=True, required=False)
    remark_type = serializers.CharField(allow_null=True, required=False)
    freetext    = serializers.CharField(allow_null=True, required=False)
    flight_ids  = serializers.ListField(child=serializers.CharField(), default=list)


class DisruptionWarningSerializer(serializers.Serializer):
    code  = serializers.CharField(allow_null=True)
    title = serializers.CharField(allow_null=True)


class PaymentRecordSerializer(serializers.Serializer):
    method         = serializers.CharField(allow_null=True)
    payment_type   = serializers.CharField(allow_null=True)
    total_amount   = serializers.IntegerField(allow_null=True)
    currency_code  = serializers.CharField()
    transaction_id = serializers.CharField(allow_null=True, required=False)


class EligibilityReasonSerializer(serializers.Serializer):
    code  = serializers.CharField(allow_null=True)
    title = serializers.CharField(allow_null=True)


class EligibilityStatusSerializer(serializers.Serializer):
    is_eligible             = serializers.BooleanField()
    non_eligibility_reasons = EligibilityReasonSerializer(many=True, default=list)


class OrderEligibilitiesSerializer(serializers.Serializer):
    cancel_and_refund = EligibilityStatusSerializer(allow_null=True, required=False)
    change            = EligibilityStatusSerializer(allow_null=True, required=False)
    seat_change       = EligibilityStatusSerializer(allow_null=True, required=False)
    service_change    = EligibilityStatusSerializer(allow_null=True, required=False)
    name_modification = EligibilityStatusSerializer(allow_null=True, required=False)
    passenger_change  = EligibilityStatusSerializer(allow_null=True, required=False)


class HeaderInfoSerializer(serializers.Serializer):
    id                          = serializers.CharField(read_only=True)
    ci_id                       = serializers.UUIDField()
    pnr                         = serializers.CharField()
    last_name                   = serializers.CharField()
    order_id                    = serializers.CharField()
    creation_date_time          = serializers.DateTimeField(allow_null=True)
    last_modification_date_time = serializers.DateTimeField(allow_null=True)
    is_group_booking            = serializers.BooleanField()
    creation_pos                = PointOfSaleSerializer(allow_null=True, required=False)
    servicing_pos               = PointOfSaleSerializer(allow_null=True, required=False)
    ticket_number               = serializers.CharField(allow_null=True)
    document_type               = serializers.CharField(allow_null=True)
    ticket_status               = serializers.CharField(allow_null=True)
    endorsement                 = serializers.CharField(allow_null=True)
    tour_code                   = serializers.CharField(allow_null=True)
    issuance_office             = serializers.CharField(allow_null=True)
    issuance_city               = serializers.CharField(allow_null=True)
    issuance_date               = serializers.DateTimeField(allow_null=True)
    payment                     = PaymentRecordSerializer(allow_null=True, required=False)
    contacts                    = ContactItemSerializer(many=True, default=list)
    remarks                     = RemarkItemSerializer(many=True, default=list)
    disruption_warning          = DisruptionWarningSerializer(allow_null=True, required=False)
    has_disruption              = serializers.BooleanField()
    order_eligibilities         = OrderEligibilitiesSerializer(allow_null=True, required=False)
    created_at                  = serializers.DateTimeField(read_only=True)
    updated_at                  = serializers.DateTimeField(read_only=True)


# ════════════════════════════════════════════════════════════
# PAX INFO
# ════════════════════════════════════════════════════════════

class PassengerNameSerializer(serializers.Serializer):
    first_name   = serializers.CharField(allow_null=True)
    last_name    = serializers.CharField(allow_null=True)
    title        = serializers.CharField(allow_null=True)
    name_type    = serializers.CharField(allow_null=True)
    is_preferred = serializers.BooleanField()


class PassportDocumentSerializer(serializers.Serializer):
    document_type         = serializers.CharField(allow_null=True)
    number                = serializers.CharField(allow_null=True)
    expiry_date           = serializers.DateTimeField(allow_null=True)
    issuance_country_code = serializers.CharField(allow_null=True)
    nationality_code      = serializers.CharField(allow_null=True)
    gender                = serializers.CharField(allow_null=True)
    birth_date            = serializers.DateTimeField(allow_null=True)
    first_name            = serializers.CharField(allow_null=True)
    last_name             = serializers.CharField(allow_null=True)


class SeatCharacteristicSerializer(serializers.Serializer):
    code = serializers.CharField(allow_null=True)
    name = serializers.CharField(allow_null=True)


class SeatAssignmentSerializer(serializers.Serializer):
    seat_id         = serializers.CharField(allow_null=True)
    flight_id       = serializers.CharField(allow_null=True)
    seat_number     = serializers.CharField(allow_null=True)
    characteristics = SeatCharacteristicSerializer(many=True, default=list)
    is_chargeable   = serializers.BooleanField()
    status_code     = serializers.CharField(allow_null=True)


class MealServiceSerializer(serializers.Serializer):
    meal_id       = serializers.CharField(allow_null=True)
    flight_id     = serializers.CharField(allow_null=True)
    meal_code     = serializers.CharField(allow_null=True)
    meal_name     = serializers.CharField(allow_null=True, required=False)
    quantity      = serializers.IntegerField()
    is_chargeable = serializers.BooleanField()
    status_code   = serializers.CharField(allow_null=True)


class SpecialServiceRequestSerializer(serializers.Serializer):
    ssr_id       = serializers.CharField(allow_null=True)
    code         = serializers.CharField(allow_null=True)
    name         = serializers.CharField(allow_null=True, required=False)
    airline_code = serializers.CharField(allow_null=True)
    status_code  = serializers.CharField(allow_null=True)
    quantity     = serializers.IntegerField()
    freetext     = serializers.CharField(allow_null=True, required=False)
    flight_ids   = serializers.ListField(child=serializers.CharField(), default=list)
    traveler_ids = serializers.ListField(child=serializers.CharField(), default=list)


class PaxInfoSerializer(serializers.Serializer):
    id                  = serializers.CharField(read_only=True)
    ci_id               = serializers.UUIDField()
    pnr                 = serializers.CharField()
    last_name           = serializers.CharField()
    traveler_id         = serializers.CharField(allow_null=True)
    passenger_type_code = serializers.CharField(allow_null=True)
    name                = PassengerNameSerializer(allow_null=True, required=False)
    passport            = PassportDocumentSerializer(allow_null=True, required=False)
    seats               = SeatAssignmentSerializer(many=True, default=list)
    meal_services       = MealServiceSerializer(many=True, default=list)
    ssrs                = SpecialServiceRequestSerializer(many=True, default=list)
    created_at          = serializers.DateTimeField(read_only=True)
    updated_at          = serializers.DateTimeField(read_only=True)


# ════════════════════════════════════════════════════════════
# FLIGHT INFO
# ════════════════════════════════════════════════════════════

class LocationDateTimeSerializer(serializers.Serializer):
    location_code = serializers.CharField(allow_null=True)
    date_time     = serializers.DateTimeField(allow_null=True)
    terminal      = serializers.CharField(allow_null=True, required=False)


class FlightStopSerializer(serializers.Serializer):
    location_code       = serializers.CharField(allow_null=True)
    airport_name        = serializers.CharField(allow_null=True, required=False)
    city                = serializers.CharField(allow_null=True, required=False)
    arrival_date_time   = serializers.DateTimeField(allow_null=True)
    departure_date_time = serializers.DateTimeField(allow_null=True)
    stop_duration       = serializers.IntegerField(allow_null=True)
    is_change_of_gauge  = serializers.BooleanField()


class DisruptionLocationDetailSerializer(serializers.Serializer):
    location_code = serializers.CharField(allow_null=True)
    same_airport  = serializers.BooleanField(allow_null=True)
    same_city     = serializers.BooleanField(allow_null=True)
    same_day      = serializers.BooleanField(allow_null=True)
    delta_time    = serializers.IntegerField(allow_null=True)


class DisruptionConnectionDetailSerializer(serializers.Serializer):
    status         = serializers.CharField(allow_null=True)
    same_via_point = serializers.BooleanField(allow_null=True)
    delta          = serializers.IntegerField(allow_null=True)
    delta_time     = serializers.IntegerField(allow_null=True)


class DisruptionStatusSerializer(serializers.Serializer):
    bound_status               = serializers.CharField(allow_null=True)
    is_in_check_in_time_window = serializers.BooleanField()
    departure                  = DisruptionLocationDetailSerializer(allow_null=True, required=False)
    arrival                    = DisruptionLocationDetailSerializer(allow_null=True, required=False)
    connection                 = DisruptionConnectionDetailSerializer(allow_null=True, required=False)
    revised_duration           = serializers.IntegerField(allow_null=True)
    original_flight_ids        = serializers.ListField(child=serializers.CharField(), default=list)


class FlightSegmentSerializer(serializers.Serializer):
    flight_id                   = serializers.CharField(allow_null=True)
    marketing_airline_code      = serializers.CharField(allow_null=True)
    airline_name                = serializers.CharField(allow_null=True, required=False)
    marketing_flight_number     = serializers.CharField(allow_null=True)
    operating_flight_number     = serializers.CharField(allow_null=True, required=False)
    cabin                       = serializers.CharField(allow_null=True)
    booking_class               = serializers.CharField(allow_null=True)
    status_code                 = serializers.CharField(allow_null=True)
    status_name                 = serializers.CharField(allow_null=True, required=False)
    fare_family_code            = serializers.CharField(allow_null=True)
    commercial_fare_family_code = serializers.CharField(allow_null=True, required=False)
    aircraft_code               = serializers.CharField(allow_null=True)
    aircraft_name               = serializers.CharField(allow_null=True, required=False)
    flight_status               = serializers.CharField(allow_null=True)
    departure                   = LocationDateTimeSerializer(allow_null=True, required=False)
    arrival                     = LocationDateTimeSerializer(allow_null=True, required=False)
    original_departure          = LocationDateTimeSerializer(allow_null=True, required=False)
    duration                    = serializers.IntegerField(allow_null=True)
    arrival_days_difference     = serializers.IntegerField()
    stops                       = FlightStopSerializer(many=True, default=list)
    is_disrupted                = serializers.BooleanField()


class AirBoundSerializer(serializers.Serializer):
    air_bound_id              = serializers.CharField(allow_null=True)
    fare_family_code          = serializers.CharField(allow_null=True)
    origin_location_code      = serializers.CharField(allow_null=True)
    origin_airport_name       = serializers.CharField(allow_null=True, required=False)
    origin_city               = serializers.CharField(allow_null=True, required=False)
    destination_location_code = serializers.CharField(allow_null=True)
    destination_airport_name  = serializers.CharField(allow_null=True, required=False)
    destination_city          = serializers.CharField(allow_null=True, required=False)
    duration                  = serializers.IntegerField(allow_null=True)
    is_disrupted              = serializers.BooleanField()
    disruption_status         = DisruptionStatusSerializer(allow_null=True, required=False)
    flights                   = FlightSegmentSerializer(many=True, default=list)


class BaggageAllowanceSerializer(serializers.Serializer):
    flight_id   = serializers.CharField(allow_null=True)
    traveler_id = serializers.CharField(allow_null=True)
    type        = serializers.CharField(allow_null=True)
    quantity    = serializers.IntegerField(allow_null=True)
    weight_kg   = serializers.IntegerField(allow_null=True, required=False)


class FlightInfoSerializer(serializers.Serializer):
    id                 = serializers.CharField(read_only=True)
    ci_id              = serializers.UUIDField()
    pnr                = serializers.CharField()
    last_name          = serializers.CharField()
    bounds             = AirBoundSerializer(many=True, default=list)
    baggage_allowances = BaggageAllowanceSerializer(many=True, default=list)
    created_at         = serializers.DateTimeField(read_only=True)
    updated_at         = serializers.DateTimeField(read_only=True)


# ════════════════════════════════════════════════════════════
# FARE INFO
# ════════════════════════════════════════════════════════════

class PricingDetailsSerializer(serializers.Serializer):
    base_fare_inr        = serializers.IntegerField(allow_null=True)
    total_taxes_inr      = serializers.IntegerField(allow_null=True)
    total_surcharges_inr = serializers.IntegerField(allow_null=True)
    grand_total_inr      = serializers.IntegerField(allow_null=True)
    currency_code        = serializers.CharField()
    taxes                = TaxItemSerializer(many=True, default=list)
    surcharges           = SurchargeItemSerializer(many=True, default=list)
    payment_method       = serializers.CharField(allow_null=True)
    payment_type         = serializers.CharField(allow_null=True)
    tour_code            = serializers.CharField(allow_null=True, required=False)


class FareBreakdownSerializer(serializers.Serializer):
    fare_info_id        = serializers.CharField(allow_null=True)
    flight_id           = serializers.CharField(allow_null=True)
    fare_class          = serializers.CharField(allow_null=True)
    fare_family_code    = serializers.CharField(allow_null=True)
    booking_class       = serializers.CharField(allow_null=True)
    coupon_status       = serializers.CharField(allow_null=True)
    base_fare_nuc       = serializers.CharField(allow_null=True)
    price_qualifier     = serializers.CharField(allow_null=True)
    baggage_type        = serializers.CharField(allow_null=True)
    baggage_quantity    = serializers.IntegerField(allow_null=True)
    flight_airline      = serializers.CharField(allow_null=True)
    flight_number       = serializers.CharField(allow_null=True)
    departure_location  = serializers.CharField(allow_null=True)
    departure_date_time = serializers.DateTimeField(allow_null=True)
    arrival_location    = serializers.CharField(allow_null=True)
    arrival_date_time   = serializers.DateTimeField(allow_null=True)


class FareElementSerializer(serializers.Serializer):
    element_id   = serializers.CharField(allow_null=True)
    code         = serializers.CharField(allow_null=True)
    text         = serializers.CharField(allow_null=True)
    flight_ids   = serializers.ListField(child=serializers.CharField(), default=list)
    traveler_ids = serializers.ListField(child=serializers.CharField(), default=list)


class FareInfoSerializer(serializers.Serializer):
    id              = serializers.CharField(read_only=True)
    ci_id           = serializers.UUIDField()
    pnr             = serializers.CharField()
    last_name       = serializers.CharField()
    ticket_number   = serializers.CharField(allow_null=True)
    traveler_id     = serializers.CharField(allow_null=True)
    pricing         = PricingDetailsSerializer(allow_null=True, required=False)
    fare_breakdowns = FareBreakdownSerializer(many=True, default=list)
    fare_elements   = FareElementSerializer(many=True, default=list)
    created_at      = serializers.DateTimeField(read_only=True)
    updated_at      = serializers.DateTimeField(read_only=True)


# ── Consolidated response serializer ─────────────────────────

class BookingResponseSerializer(serializers.Serializer):
    ci_id     = serializers.UUIDField()
    pnr       = serializers.CharField()
    last_name = serializers.CharField()
    header    = HeaderInfoSerializer(required=False)
    pax       = PaxInfoSerializer(required=False)
    flight    = FlightInfoSerializer(required=False)
    fare      = FareInfoSerializer(required=False)
