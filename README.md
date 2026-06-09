# skyler

> Adi Cohen - 213526213

"Hi! I am an AI-powered chatbot using the Booking API and natural language processing to assist in finding the right flight for you."

This project was developed as part of the Natural Language Processing (NLP) course at the Holon Institute of Technology (HIT) during the Spring 2026 semester. It demonstrates the integration of Google Dialogflow ES, Python, and the Booking.com Flights API to create an intelligent travel assistant.

## Table of Contents

- [Introduction](#introduction)
- [Functionality](#functionality)
- [Project Overview](#project-overview)
- [Dialogflow Agent](#dialogflow-agent)
- [Python Client](#python-client)
- [Booking API](#booking-api)
- [Discussion](#discussion)
- [Closing Remarks](#closing-remarks)

---

## Introduction

skyler is a conversational AI application that simplifies the process of searching for flights. Instead of manually navigating travel websites, users can simply chat with the assistant in natural language and provide the information needed to find suitable flights.

The chatbot is built using Google Dialogflow ES for natural language understanding and a Python client that communicates with the Booking API to retrieve flight information.

The main objective of this project is to demonstrate how Natural Language Processing (NLP) can be integrated with external APIs to create an interactive and user-friendly travel assistant.

## Functionality

skyler will ask you about all the details needed, such as where you want to fly to, what your departure airport is, and how many adults you wish to book the flight for. Then, it will present the ten most suitable flights for you, including their actual prices. On top of that, the user can choose between three different sorting options (best, cheapest, fastest) to get a better overview of the found flights. After choosing a flight, there's a deeplink the user may open to actually finish the booking and pay for the flight.

But why should anyone even bother using skyler instead of using Booking.com directly? Websites are typically filled with ads and distracting content. skyler just wants to help you with your flight, cuts out all the clutter, and helps guide you through the process easily.

We envision being able to talk to skyler in the future to fully realize its potential and usability, since talking is much more convenient than typing.

### Conversation Snippet
Here is what a conversation with skyler might look like:
![Conversation Snippet](img/Example_Conversation.png)

## Project Overview

skyler is made of three parts. The Python client is the frontend, which communicates with Dialogflow and Booking in the backend. Users will not notice any of the backend parts involved, but will only interact with skyler through their terminal. 

![Sequence Diagram](img/Sequence_Diagram.png)

The user interacts with the Python client through a terminal. The input of the user is typically forwarded to Dialogflow to figure out its intent. Dialogflow's answer is then prompted to the user in the terminal of the Python client. Eventually, skyler's Dialogflow part gathered all the info needed in order to perform a Booking API call. 

## Dialogflow Agent

### Intents
![Dialogflow Intents](img/Intents.png)

The preceding figure shows the intents configured to book a flight with skyler. To map the intent structure and the purpose of each intent, the following flowchart clarifies the dependencies and the context flow:

![Flowchart of the Dialogflow Intents](img/figure4.png)

### Entities
Google Cloud Dialogflow utilizes Named Entity Recognition (NER) to automatically detect and extract key variables from unstructured text. skyler relies on the following built-in system entities:
* **`@sys.number`** – Parses passenger counts into integers.
* **`@sys.date-time`** – Normalizes natural language dates into query-ready timestamps.
* **`@sys.airport`** – Maps airport names to 3-letter IATA codes.
* **`@sys.currency-name`** – Identifies ISO currency preferences for financial consistency.

## Python Client

The Python runtime engine (`client.py`) serves as the central stateful orchestrator. It acts as an abstraction layer that manages data transitions between the user's terminal, the Dialogflow NLP engine, and the Booking.com REST APIs.

![Start of Conversation](img/Start_of_Conversation.png)

The client handles the conversation loop and, once the required intent is reached, triggers the network request to the Booking API. It also handles the extraction of parameters from the Dialogflow context:

![Parameter Extraction Code](img/Parameters.png)

## Booking API
The flight aggregation core is powered by the **Booking.com Flights API** via RapidAPI. Once all slot-filling requirements are satisfied, `client.py` invokes the `fetchFlights()` routine. This executes an authenticated RESTful HTTP `GET` request and maps the nested JSON response directly into our terminal interface.

![Live JSON Payload](img/booking_payload.png)

## Discussion
Google's Dialogflow is a good fit for this project due to its maturity and documentation. However, we learned that changing context parameters can be challenging for the visual representation of the intent structure. While Dialogflow occasionally struggles with nuances, using it for this project was essential, as building this logic from scratch in Python alone would have been impractical.

## Closing Remarks
Contrary to our initial beliefs, the capabilities of AI in this form are still relatively limited by the predefined data structures of external APIs. Nevertheless, chatbots have great potential in filtering intent from natural language, saving users from manual navigation. Looking back, we definitely learned a lot about integrating cloud services, and we are very happy with the final results of our work.
