from django.dispatch import Signal

action = Signal(providing_args=['actor','verb','target','created_at','project','company','private_action'])