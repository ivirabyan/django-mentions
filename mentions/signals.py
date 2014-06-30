from django.dispatch import Signal

objects_mentioned = Signal(providing_args=['mentions', 'instance', 'created'])
