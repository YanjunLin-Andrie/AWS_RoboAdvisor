### Required Libraries ###
from datetime import datetime

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

def validate_data(age, investment_amount, intent_request):
    """
    Validates the data provided by the user.
    """    
    # Validate the retirement age based on the user's current age.
    if age:
        age = parse_int(age)  # Cast string to int values
        if age < 0:
            return build_validation_result(
               False,
               "age",
               "Your age is invalid, can you provide an age greater than zero?",
           )
        elif age >= 65:
            return build_validation_result(
               False,
               "age",
               "The maximum age to contract this service is 64, "
               "can you provide an age between 0 and 64 please?",
           )
    # Validate user's investment amount
    if investment_amount is not None:
        investment_amount = parse_int(investment_amount)
        if investment_amount < 5000:
            return build_validation_result(
                    False,
                    "investment_amount",
                    "Please enter an amount greater than 5000 to see results.",
                )
    
    # A True results is returned if age or amount are valid
    return build_validation_result(True, None, None)


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """
    # Gets slots' values
    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    
    # Gets the invocation source, for Lex dialogs "DialogCodeHook" is expected.
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # This code performs basic validation on the supplied input slots.

        # Gets all the slots
        slots = get_slots(intent_request)

        # Validates user's input using the validate_data function
        validation_result = validate_data(age, investment_amount, intent_request)

        # If the data provided by the user is not valid,
        # the elicitSlot dialog action is used to re-prompt for the first violation detected.
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None  # Cleans invalid slot

            # Returns an elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )

        # Fetch current session attributes
        output_session_attributes = intent_request["sessionAttributes"]

        # Once all slots are valid, a delegate dialog is returned to Lex to choose the next course of action.
        return delegate(output_session_attributes, get_slots(intent_request))

     # Return a message with conversion's result.
    if risk_level == 'None':
        return close(
            intent_request["sessionAttributes"],
            "Fulfilled",
            {
                "contentType": "PlainText",
                "content": """Thank you for your information;
                With no risk level, you investment recommendation is: 100% bonds (AGG), 0% equities (SPY).
                """
            },
        )
    elif risk_level == 'Low':
        return close(
            intent_request["sessionAttributes"],
            "Fulfilled",
            {
                "contentType": "PlainText",
                "content": """Thank you for your information;
                With Low risk level, you investment recommendation is: 60% bonds (AGG), 40% equities (SPY).
                """
            },
        )
    elif risk_level == 'Medium':
        return close(
            intent_request["sessionAttributes"],
            "Fulfilled",
            {
                "contentType": "PlainText",
                "content": """Thank you for your information;
                With Medium risk level, you investment recommendation is: 40% bonds (AGG), 60% equities (SPY).
                """
            },
        )
    elif risk_level == 'High':
        return close(
            intent_request["sessionAttributes"],
            "Fulfilled",
            {
                "contentType": "PlainText",
                "content": """Thank you for your information;
                With High risk level, you investment recommendation is: 20% bonds (AGG), 80% equities (SPY).
                """
            },
        )
    

        
### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "recommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
