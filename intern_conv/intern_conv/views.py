import json
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from google.auth import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauth2_provider.views.generic import ProtectedResourceView

class GoogleCalendarInitView(View):
    def get(self, request):
        # Define the scopes required for calendar access
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

        # Set up the OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            SCOPES,
            redirect_uri=request.build_absolute_uri(reverse('calendar_redirect'))
        )

        # Generate the authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        # Store the state in the session for later verification
        request.session['oauth_state'] = state

        # Redirect the user to the authorization URL
        return redirect(authorization_url)

class GoogleCalendarRedirectView(View):
    def get(self, request):
        # Verify the state to prevent CSRF attacks
        state = request.session.get('oauth_state', None)
        if state is None or state != request.GET.get('state'):
            return redirect(reverse('calendar_init'))

        # Set up the OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri(reverse('calendar_redirect'))
        )

        # Exchange the authorization code for an access token
        flow.fetch_token(
            authorization_response=request.build_absolute_uri(),
        )

        # Get the access token
        credentials = flow.credentials
        access_token = credentials.token

        # Build the Google Calendar API client
        service = build('calendar', 'v3', credentials=credentials)

        # Retrieve the list of events from the user's calendar
        events = service.events().list(calendarId='primary').execute()

        # table = '<table>'
        # table += '<tr><th>Summary</th><th>Start</th><th>End</th></tr>'
        # for event in events.get('items', []):
        #    summary = event.get('summary', 'N/A')
        #    start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'N/A'))
        #    end = event.get('end', {}).get('dateTime', event.get('end', {}).get('date', 'N/A'))
        #    table += f'<tr><td>{summary}</td><td>{start}</td><td>{end}</td></tr>'
        # table += '</table>'
        # Process the events as per your requirements

        return HttpResponse(json.dumps(events, indent=2))# Return the response for the events (e.g., serialize and return as JSON)
        # return HttpResponse(table)