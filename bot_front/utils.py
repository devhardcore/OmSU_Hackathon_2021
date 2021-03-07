from backend.entity import Event


def event_to_str(event: Event):
    return "\n".join([f"Название события: {event.name.get('text')}",
                      f"Описание события: {event.summary}",
                      f"Количество мест: {event.capacity}",
                      f"Дата начала: {event.start.get('local')}",
                      f"Дата конца мероприятия: {event.start.get('local')}"
                      ])
