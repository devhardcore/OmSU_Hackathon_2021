import datetime
import logging

import pytz
from eventbrite import Eventbrite

from backend.entity import Event

eventbrite_service = Eventbrite("5TI53UYTLBEHI77L6J3G")


def get_organization_id(service):
    data = service.get("https://www.eventbriteapi.com/v3/users/me/organizations/")
    organization_id = data["organizations"][0]["id"]
    return organization_id


def set_tickets(service: Eventbrite, event_id: int, capacity: int):
    r = service.post(path=f"https://www.eventbriteapi.com/v3/events/{event_id}/ticket_classes/", data={
        "ticket_class": {
            "name": "VIP",
            "quantity_total": capacity,
            "free": True
        }
    })


def push_event(service, name, start, end, summary, count):
    local = pytz.timezone("Asia/Omsk")
    org_id = get_organization_id(service)
    start_obj = datetime.datetime.strptime(start, '%d-%m-%Y %H:%M')
    end_obj = datetime.datetime.strptime(end, '%d-%m-%Y %H:%M')
    utc_start = local.localize(start_obj, is_dst=None)
    utc_end = local.localize(end_obj, is_dst=None)
    utc_start = utc_start.astimezone(pytz.utc)
    utc_end = utc_end.astimezone(pytz.utc)
    ret = service.post(path=f"https://www.eventbriteapi.com/v3/organizations/{org_id}/events/", data={
        "event": {
            "name": {
                "html": name
            },
            "summary": summary[:140],
            "start": {
                "timezone": "Asia/Omsk",
                "utc": utc_start.strftime("%Y-%m-%dT%H:%M:00Z")
            },
            "end": {
                "timezone": "Asia/Omsk",
                "utc": utc_end.strftime("%Y-%m-%dT%H:%M:00Z")
            },
            "capacity": count,
            "currency": "USD"
        }
    })
    event_id = ret.get("id")
    set_tickets(service, event_id, ret.get("capacity"))
    logging.info(f"Event was created! {ret}")
    service.post(path=f"https://www.eventbriteapi.com/v3/events/{event_id}/publish/")


def get_all_events(service, organization_id):
    data = service.get(path=f"https://www.eventbriteapi.com/v3/organizations/{organization_id}/events")
    events = []
    for event in data.get('events'):
        name = event.get("name")
        description = event.get("summary")
        start = event.get("start")
        end = event.get("end")
        event_id = event.get("id")
        capacity = event.get("capacity")
        url = event.get("url")
        events.append(
            Event(name=name, summary=description, start=start, end=end, event_id=event_id, capacity=capacity, url=url))
    return events
