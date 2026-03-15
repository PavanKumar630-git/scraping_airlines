// ============================================================
// MongoDB Flight Booking Data - Structured Insert Script
// Collections: HeaderInfo, PaxInfo, FlightInfo, FareInfo
// Common Key: ci_id (UUID) + pnr + last_name
// ============================================================

const { MongoClient } = require("mongodb");
const { v4: uuidv4 } = require("uuid");

// ─── Common Keys ────────────────────────────────────────────
const ci_id = uuidv4();           // e.g. "a1b2c3d4-e5f6-..."  — shared across ALL collections
const pnr = "98RZ64";
const lastName = "PUROHIT";

// ============================================================
// 1. HEADER INFO
// ============================================================
const headerInfo = {
    ci_id,
    pnr,
    lastName,

    orderId: "98RZ64",
    creationDateTime: new Date("2026-02-18T08:02:00.000Z"),
    lastModificationDateTime: new Date("2026-03-05T12:02:00.000Z"),
    isGroupBooking: false,

    creationPointOfSale: {
        pointOfSaleId: "DELC32326",
        countryCode: "IN"
    },
    servicingPointOfSale: {
        pointOfSaleId: "DELAI08AA",
        countryCode: "IN"
    },

    ticketNumber: "0985013887401",
    documentType: "eticket",
    ticketStatus: "ISSUED",
    endorsement: "NON-END/CHANGE CANCELLATION/NO-SHOW PENALTY MAY APPLY AS PER FARE RULES -BG AI",
    tourCode: "AISME002",
    issuanceOffice: "QJUI228BK",
    issuanceCity: "QJU",
    issuanceDate: new Date("2026-02-19T00:00:00.000+05:30"),

    payment: {
        method: "CASH",
        paymentType: "CustomPayment",
        totalAmountINR: 592699
    },

    contacts: [
        {
            id: "OT5",
            category: "other",
            contactType: "Phone",
            deviceType: "landline",
            purpose: "standard",
            number: "DEL 23415261/23411309/23414053 - BIRDS WING - A"
        },
        {
            id: "OT23",
            category: "other",
            contactType: "Email",
            purpose: "standard",
            address: "SECURED DATA"
        },
        {
            id: "OT13",
            category: "other",
            contactType: "Phone",
            deviceType: "mobile",
            purpose: "notification",
            countryPhoneExtension: "91",
            number: "9810187747"
        }
    ],

    remarks: [
        {
            id: "OT45",
            remarkType: "GeneralRemark",
            freetext: "WHATSAPP NOTIFICATION SENT 919810187747 05MAR26 11:59:00 INVOLUNTARY CHANGE IN STD."
        },
        {
            id: "OT46",
            remarkType: "GeneralRemark",
            freetext: "SMS NOTIFICATION SENT 234152612341130923414053 05MAR26 12:01:00 INVOLUNTARY CHANGE IN STD."
        },
        {
            id: "OT4",
            remarkType: "GeneralRemark",
            freetext: "NOTIFY PASSENGER PRIOR TO TICKET PURCHASE & CHECK-IN: FEDERAL LAWS FORBID THE CARRIAGE OF HAZARDOUS MATERIALS - GGAMAUSHAZ",
            flightIds: ["ST1", "ST2"]
        }
    ],

    disruptionWarning: {
        code: "65227",
        title: "FLIGHT DISRUPTION HAS OCCURRED: CHECK THE ORDER CONTENT"
    },

    orderEligibilities: {
        cancelAndRefund: {
            isEligible: false,
            reason: "Voluntary refund not possible on disrupted flights."
        },
        change: {
            isEligible: false,
            reason: "DISRUPTED ORDER"
        },
        seatChange: {
            isEligible: false,
            reason: "SEAT CHANGE NOT ALLOWED / DISRUPTED ORDER"
        },
        serviceChange: {
            isEligible: false,
            reason: "DISRUPTED ORDER"
        }
    },

    createdAt: new Date(),
    updatedAt: new Date()
};

// ============================================================
// 2. PAX INFO  (Passenger Information)
// ============================================================
const paxInfo = {
    ci_id,
    pnr,
    lastName,

    travelerId: "PT1",
    passengerTypeCode: "ADT",

    name: {
        firstName: "Arun Kumar",
        lastName: "Purohit",
        title: "MR",
        nameType: "universal",
        isPreferred: true
    },

    passport: {
        documentType: "passport",
        number: "X3454032",
        expiryDate: new Date("2034-02-04"),
        issuanceCountryCode: "IND",
        nationalityCode: "IN",
        gender: "male",
        birthDate: new Date("1952-08-15"),
        firstName: "ARUN KUMAR MR",
        lastName: "PUROHIT"
    },

    specialServiceRequests: [
        {
            id: "OT14",
            code: "AVML",
            name: "Asian Vegetarian Meal Request",
            airlineCode: "AI",
            statusCode: "HK",
            quantity: 1,
            flightIds: ["ST1"]
        },
        {
            id: "OT15",
            code: "AVML",
            name: "Asian Vegetarian Meal Request",
            airlineCode: "AI",
            statusCode: "HK",
            quantity: 1,
            flightIds: ["ST2"]
        },
        {
            id: "OT13",
            code: "CTCM",
            airlineCode: "AI",
            statusCode: "HK",
            quantity: 1,
            freetext: "919810187747"
        },
        {
            id: "OT24",
            code: "DOCS",
            name: "PASSENGER/CREW PRIMARY TRAVEL DOCUMENT INFO",
            airlineCode: "AI",
            statusCode: "HK",
            quantity: 1,
            freetext: "P/IND/X3454032/IN/15AUG52/M/04FEB34/PUROHIT/ARUN KUMAR MR"
        }
    ],

    seats: [
        {
            id: "OT16",
            flightId: "ST1",
            seatNumber: "5A",
            characteristics: ["No smoking", "Window seat", "Aisle seat"],
            isChargeable: false,
            statusCode: "HK"
        },
        {
            id: "OT19",
            flightId: "ST2",
            seatNumber: "8C",
            characteristics: ["No smoking", "Aisle seat"],
            isChargeable: false,
            statusCode: "HK"
        }
    ],

    mealServices: [
        {
            id: "OT14",
            flightId: "ST1",
            mealCode: "AVML",
            quantity: 1,
            isChargeable: false,
            statusCode: "HK"
        },
        {
            id: "OT15",
            flightId: "ST2",
            mealCode: "AVML",
            quantity: 1,
            isChargeable: false,
            statusCode: "HK"
        }
    ],

    createdAt: new Date(),
    updatedAt: new Date()
};

// ============================================================
// 3. FLIGHT INFO
// ============================================================
const flightInfo = {
    ci_id,
    pnr,
    lastName,

    bounds: [
        {
            airBoundId: "1",
            fareFamilyCode: "BUSVALU",
            originLocationCode: "DEL",
            originAirportName: "INDIRA GANDHI INTL",
            originCity: "DELHI",
            destinationLocationCode: "JFK",
            destinationAirportName: "JOHN F KENNEDY INTL",
            destinationCity: "NEW YORK",
            duration: 62400,       // seconds
            isDisrupted: false,

            flights: [
                {
                    flightId: "ST1",
                    marketingAirlineCode: "AI",
                    airlineName: "AIR INDIA",
                    marketingFlightNumber: "101",
                    operatingFlightNumber: "101",
                    cabin: "business",
                    bookingClass: "J",
                    statusCode: "HK",
                    statusName: "Holding confirmed",
                    fareFamilyCode: "BUSVALU",
                    aircraftCode: "359",
                    aircraftName: "AIRBUS A350-900",
                    flightStatus: "scheduled",

                    departure: {
                        locationCode: "DEL",
                        dateTime: new Date("2026-03-22T02:00:00.000+05:30"),
                        terminal: "3"
                    },
                    arrival: {
                        locationCode: "JFK",
                        dateTime: new Date("2026-03-22T09:50:00.000-04:00"),
                        terminal: "4"
                    },
                    duration: 62400,
                    stops: [],
                    arrivalDaysDifference: 0
                }
            ]
        },
        {
            airBoundId: "2QUlf838613f2e8",
            fareFamilyCode: "BUSVALU",
            originLocationCode: "SFO",
            originAirportName: "SAN FRANCISCO INTL",
            originCity: "SAN FRANCISCO",
            destinationLocationCode: "DEL",
            destinationAirportName: "INDIRA GANDHI INTL",
            destinationCity: "DELHI",
            duration: 72000,
            isDisrupted: true,

            disruptionStatus: {
                boundStatus: "disrupted",
                isInCheckInTimeWindow: false,
                departure: {
                    locationCode: "SFO",
                    sameAirport: true,
                    sameCity: true,
                    sameDay: true,
                    deltaTime: 1800       // 30 min delay
                },
                arrival: {
                    locationCode: "DEL",
                    sameAirport: true,
                    sameCity: true,
                    sameDay: true,
                    deltaTime: 0
                },
                connection: {
                    status: "ok",
                    sameViaPoint: true,
                    delta: 0
                },
                revisedDuration: 73800
            },

            flights: [
                {
                    flightId: "ST2",
                    marketingAirlineCode: "AI",
                    airlineName: "AIR INDIA",
                    marketingFlightNumber: "174",
                    operatingFlightNumber: "174",
                    cabin: "business",
                    bookingClass: "Z",
                    statusCode: "TK",
                    statusName: "Confirmed, timechange",
                    fareFamilyCode: "BUSVALU",
                    aircraftCode: "77W",
                    aircraftName: "BOEING 777-300ER",
                    flightStatus: "scheduled",

                    departure: {
                        locationCode: "SFO",
                        dateTime: new Date("2026-04-04T10:30:00.000-07:00"),   // revised time
                        originalDateTime: new Date("2026-04-04T10:00:00.000-07:00"),
                        terminal: "I"
                    },
                    arrival: {
                        locationCode: "DEL",
                        dateTime: new Date("2026-04-05T19:00:00.000+05:30"),
                        terminal: "3"
                    },
                    duration: 72000,
                    arrivalDaysDifference: 1,
                    stops: [
                        {
                            locationCode: "CCU",
                            airportName: "SUBHAS CHANDRA BOSE",
                            city: "KOLKATA",
                            arrivalDateTime: new Date("2026-04-05T16:00:00.000+05:30"),
                            departureDateTime: new Date("2026-04-05T16:35:00.000+05:30"),
                            stopDuration: 2100,
                            isChangeOfGauge: false
                        }
                    ]
                }
            ]
        }
    ],

    baggageAllowance: [
        {
            flightId: "ST1",
            travelerId: "PT1",
            type: "piece",
            quantity: 2
        },
        {
            flightId: "ST2",
            travelerId: "PT1",
            type: "piece",
            quantity: 2
        }
    ],

    createdAt: new Date(),
    updatedAt: new Date()
};

// ============================================================
// 4. FARE INFO
// ============================================================
const fareInfo = {
    ci_id,
    pnr,
    lastName,

    ticketNumber: "0985013887401",
    travelerId: "PT1",

    pricing: {
        baseFareINR: 466735,
        totalTaxesINR: 98434,
        totalSurchargesINR: 27530,
        grandTotalINR: 592699,
        currencyCode: "INR",

        taxes: [
            { code: "IN", value: 1363, description: "India" },
            { code: "K3", value: 88968, description: "K3CB" },
            { code: "P2", value: 1285, description: "P2AF" },
            { code: "AY", value: 508, description: "AYSE" },
            { code: "US", value: 2123, description: "USAP" },
            { code: "US", value: 2123, description: "USAS" },
            { code: "XA", value: 349, description: "XACO" },
            { code: "XY", value: 635, description: "XYCR" },
            { code: "YC", value: 671, description: "YCAE" },
            { code: "XF", value: 409, description: "XF" }
        ],

        surcharges: [
            { code: "YQ", value: 27210, description: "YQAC" },
            { code: "YR", value: 320, description: "YRVA" }
        ],

        paymentMethod: "CASH",
        paymentType: "CustomPayment",
        conditions: {
            tourCode: "AISME002"
        }
    },

    fareBreakdowns: [
        {
            fareInfoId: "fareInfo-1",
            flightId: "ST1",
            fareClass: "JK2CW7DY",
            fareFamilyCode: "BUSVALU",
            bookingClass: "J",
            couponStatus: "open",
            baseFareNUC: "1742.60",
            priceQualifier: "BASE_FARE",
            baggageAllowance: { type: "piece", quantity: 2 },
            flight: {
                airline: "AI",
                flightNumber: "101",
                departure: {
                    locationCode: "DEL",
                    dateTime: new Date("2026-03-22T02:00:00.000+05:30")
                },
                arrival: {
                    locationCode: "JFK",
                    dateTime: new Date("2026-03-22T09:50:00.000-04:00")
                }
            }
        },
        {
            fareInfoId: "fareInfo-3",
            flightId: "ST2",
            fareClass: "ZL2CW7DY",
            fareFamilyCode: "BUSVALU",
            bookingClass: "Z",
            couponStatus: "open",
            baseFareNUC: "1639.77",
            priceQualifier: "BASE_FARE",
            baggageAllowance: { type: "piece", quantity: 2 },
            flight: {
                airline: "AI",
                flightNumber: "174",
                departure: {
                    locationCode: "SFO",
                    dateTime: new Date("2026-04-04T10:00:00.000-07:00")
                },
                arrival: {
                    locationCode: "DEL",
                    dateTime: new Date("2026-04-05T19:00:00.000+05:30")
                }
            }
        }
    ],

    fareElements: [
        {
            id: "OT31",
            code: "FT",
            text: "PAX *F*AISME002",
            flightIds: ["ST1", "ST2"]
        }
    ],

    createdAt: new Date(),
    updatedAt: new Date()
};

// ============================================================
// INSERT INTO MONGODB
// ============================================================
async function insertFlightBooking() {
    const uri = process.env.MONGO_URI || "mongodb://localhost:27017";
    const client = new MongoClient(uri);

    try {
        await client.connect();
        const db = client.db("flight_bookings");

        // Insert all 4 collections
        await db.collection("HeaderInfo").insertOne(headerInfo);
        console.log("✅ HeaderInfo inserted  | ci_id:", ci_id);

        await db.collection("PaxInfo").insertOne(paxInfo);
        console.log("✅ PaxInfo inserted     | ci_id:", ci_id);

        await db.collection("FlightInfo").insertOne(flightInfo);
        console.log("✅ FlightInfo inserted  | ci_id:", ci_id);

        await db.collection("FareInfo").insertOne(fareInfo);
        console.log("✅ FareInfo inserted    | ci_id:", ci_id);

        console.log("\n🎯 All records share:");
        console.log("   ci_id    :", ci_id);
        console.log("   pnr      :", pnr);
        console.log("   lastName :", lastName);

    } catch (err) {
        console.error("❌ Error inserting documents:", err);
    } finally {
        await client.close();
    }
}

insertFlightBooking();