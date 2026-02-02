from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
from app.core.config import settings
from app.services.google_auth import GoogleAuthService

class CalendarService:
    """Handles all Google Calendar operations"""
    
    def __init__(self, token_data: Dict[str, Any]):
        """Initialize with user's OAuth token"""
        self.credentials = GoogleAuthService.get_credentials_from_token(token_data)
        self.service = build('calendar', 'v3', credentials=self.credentials)
    
    def generate_review_dates(self, start_date: date, intervals: List[int]) -> List[date]:
        """
        Generate review dates based on StudyCore intervals.
        
        Args:
            start_date: The date to start from
            intervals: List of days to add (e.g., [1, 3, 7, 21])
        
        Returns:
            List of review dates
        """
        return [start_date + timedelta(days=interval) for interval in intervals]
    
    def create_review_event(
        self,
        topic: str,
        review_date: date,
        interval_days: int,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Create a single all-day review event in Google Calendar.
        
        Args:
            topic: The subject/topic being reviewed
            review_date: Date for the review
            interval_days: Number of days since initial learning
            calendar_id: Google Calendar ID (default: 'primary')
        
        Returns:
            Created event data from Google Calendar API
        """
        event = {
            'summary': f'Review: {topic}',
            'description': (
                f'Spaced repetition review for: {topic}\n\n'
                f'Interval: {interval_days} day{"s" if interval_days != 1 else ""}\n'
                f'Review this material to strengthen long-term retention.\n\n'
                f'Created by StudyCore'
            ),
            'start': {
                'date': review_date.isoformat(),
                'timeZone': settings.TIMEZONE
            },
            'end': {
                'date': review_date.isoformat(),
                'timeZone': settings.TIMEZONE
            },
            'reminders': {
                'useDefault': True,  # Use calendar's default reminders
            },
            'colorId': '9'  # Blue color for study events
        }
        
        created_event = self.service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()
        
        return created_event
    
    def create_full_schedule(
        self,
        topic: str,
        start_date: date,
        intervals: List[int],
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Create a complete StudyCore schedule.
        
        Args:
            topic: The subject being studied
            start_date: When to start the review schedule
            intervals: Days between reviews (e.g., [1, 3, 7, 21])
            calendar_id: Target Google Calendar
        
        Returns:
            Dictionary with review dates and created event IDs
        """
        review_dates = self.generate_review_dates(start_date, intervals)
        created_events = []
        
        for review_date, interval in zip(review_dates, intervals):
            try:
                event = self.create_review_event(
                    topic=topic,
                    review_date=review_date,
                    interval_days=interval,
                    calendar_id=calendar_id
                )
                created_events.append({
                    'date': review_date.isoformat(),
                    'interval': interval,
                    'event_id': event['id'],
                    'event_link': event['htmlLink']
                })
            except Exception as e:
                # Log error but continue with other events
                print(f"Error creating event for {review_date}: {str(e)}")
                created_events.append({
                    'date': review_date.isoformat(),
                    'interval': interval,
                    'error': str(e)
                })
        
        return {
            'topic': topic,
            'start_date': start_date.isoformat(),
            'intervals': intervals,
            'review_dates': [d.isoformat() for d in review_dates],
            'events': created_events,
            'total_created': len([e for e in created_events if 'event_id' in e]),
            'total_failed': len([e for e in created_events if 'error' in e])
        }
    
    def delete_event(self, event_id: str, calendar_id: str = 'primary'):
        """Delete a calendar event"""
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting event {event_id}: {str(e)}")
            return False
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """Get list of user's calendars"""
        calendars_result = self.service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        
        return [
            {
                'id': cal['id'],
                'name': cal['summary'],
                'primary': cal.get('primary', False)
            }
            for cal in calendars
        ]
