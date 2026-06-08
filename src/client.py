import os
from google.cloud import dialogflow
from ApiHandler import *
from rich.table import Table
from rich.console import Console

console = Console()

# Path to active project key-file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './skylerproject-u9os-82ab9724341d.json'
LANGUAGE_CODE = "en"


if __name__ == "__main__":
    user_name = input("skyler: Hey there 👋 Please enter your name: ")

    print(f"skyler: Hi {user_name}, I am an AI-powered chatbot using the Booking API and natural language "
          f"processing to assist in finding the right flight for you.")

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path('skylerproject-u9os', 'live_synchronized_session')

    while True:
        user_text = input(f"{user_name}: ")
        
        if user_text.lower() in ['exit', 'quit', 'bye']:
            print("skyler: Safe travels! Goodbye!")
            break

        text_input = dialogflow.TextInput(text=user_text, language_code=LANGUAGE_CODE)
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        print("skyler: " + response.query_result.fulfillment_text)
        
        action_name = response.query_result.action

        if action_name == 'execute_flight_search':
            
            all_values = {}
            for context in response.query_result.output_contexts:
                if context.parameters:
                    for key in context.parameters.keys():
                        val = context.parameters.get(key)
                        if hasattr(val, 'items'):
                            all_values[key] = dict(val.items())
                        else:
                            all_values[key] = val

            sort_order_param = all_values.get('sort-order') if all_values.get('sort-order') else 'best'
            currency = all_values.get('currency', 'ILS')
            adults = int(all_values.get('adults', 1))
            children = int(all_values.get('child', 0))
            cabin_class = all_values.get('cabin_class', 'economy')
            
            from_date = all_values.get('departure_date')
            return_date = all_values.get('return_date')
            
            from_airport_obj = all_values.get('departure_airport', {})
            to_airport_obj = all_values.get('destination_airport', {})
            
            from_airport = from_airport_obj.get('IATA') if isinstance(from_airport_obj, dict) else from_airport_obj
            to_airport = to_airport_obj.get('IATA') if isinstance(to_airport_obj, dict) else to_airport_obj

            from_airport = str(from_airport) if from_airport else ""
            to_airport = str(to_airport) if to_airport else ""

            if isinstance(from_date, str) and 'T' in from_date:
                from_date = from_date.split('T')[0]
            if isinstance(return_date, str) and 'T' in return_date:
                return_date = return_date.split('T')[0]
                
            all_flights, legs, carriers, sortingOptions, agents = fetchFlights(
                from_airport, to_airport, currency=currency, adults=adults, 
                children=children, from_date=from_date, return_date=return_date, cabin_class=cabin_class
            )

            if not sortingOptions or not sortingOptions.get(sort_order_param):
                print(f"skyler: No scheduling options available for metric preference '{sort_order_param}'.")
                continue

            flight_list = []
            for sort in sortingOptions.get(sort_order_param):
                used_legs = list(map(lambda it: legs.get(it), all_flights.get(sort.get('itineraryId')).get('legIds')))

                pricing_options = list(map(lambda po: list(map(lambda p: {'price': p.get('price'), 'agent': agents.get(p.get('agentId')).get('name'), 'deepLink': p.get('deepLink')}, po.get('items'))), all_flights.get(sort.get('itineraryId')).get('pricingOptions')))
                pricing_options = [item for sublist in pricing_options for item in sublist] # Flatten list

                for leg in used_legs:
                    if not leg:
                        continue
                    found_flight = {}
                    found_flight['departureDateTime'] = leg.get('departureDateTime')
                    found_flight['arrivalDateTime'] = leg.get('arrivalDateTime')
                    found_flight['durationInMinutes'] = leg.get('durationInMinutes')
                    found_flight['stopCount'] = leg.get('stopCount')
                    found_flight['operatingCarrierIds'] = list(map(lambda cId: carriers.get(cId).get('name') if carriers.get(cId) else 'Unknown', leg.get('operatingCarrierIds')))
                    found_flight['pricingOptions'] = pricing_options
                    
                    flight_list.append(found_flight)

            top_ten_results = flight_list[0:10]

            table = Table(show_header=True, header_style='bold yellow')
            table.add_column('Price')
            table.add_column('Stop Count')
            table.add_column('Duration')
            table.add_column('Airline(s)')
            table.add_column('From')
            table.add_column('Departure Date')
            table.add_column('Departure Time')
            table.add_column('To')
            table.add_column('Arrival Date')
            table.add_column('Arrival Time')
            table.add_column('Link to finish the booking process')
            
            get_date = lambda d: "{0:0>2}".format(d.get('day')) + '.' + "{0:0>2}".format(d.get('month')) + '.' + str(d.get('year')) if isinstance(d, dict) else str(d)
            get_time = lambda d: "{0:0>2}".format(d.get('hour')) + ':' + "{0:0>2}".format(d.get('minute')) if isinstance(d, dict) else str(d)

            for row in top_ten_results:
                duration_hours = int(row.get('durationInMinutes') / 60)
                duration_minutes = row.get('durationInMinutes') % 60
                duration_text = f"{duration_hours}h {duration_minutes}min"
                
                price = '\n or '.join(list(map(lambda po: str(float(po.get('price').get('amount') or 0) / 1000) + ' ' + currency + ' on ' + po.get('agent'), row.get('pricingOptions'))))
                hyperLinks = '\n or '.join(list(map(lambda po: f'[link={po.get("deepLink")}]{po.get("agent")}[/link]', row.get('pricingOptions'))))
                
                departureDate = get_date(row.get('departureDateTime'))
                departureTime = get_time(row.get('departureDateTime'))
                operatingCarrierIds = ', '.join(row.get('operatingCarrierIds'))
                arrivalDate = get_date(row.get('arrivalDateTime'))
                arrivalTime = get_time(row.get('arrivalDateTime'))
                
                from_airport_name = from_airport_obj.get('name') if isinstance(from_airport_obj, dict) else from_airport
                to_airport_name = to_airport_obj.get('name') if isinstance(to_airport_obj, dict) else to_airport
                
                stopCount = row.get('stopCount')
                table.add_row(f'[red]{price}', f'[red]{stopCount}', f'[magenta]{duration_text}', f'[magenta]{operatingCarrierIds}', str(from_airport_name), f'[yellow]{departureDate}', f'[yellow]{departureTime}', str(to_airport_name), f'[blue]{arrivalDate}', f'[blue]{arrivalTime}', hyperLinks)
            
            console.print(table)