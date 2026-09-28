import contextvars

client_ip_var: contextvars.ContextVar[str] = contextvars.ContextVar("client_ip", default="")


def get_client_ip() -> str:
    return client_ip_var.get()


def set_client_ip(ip: str):
    client_ip_var.set(ip)
