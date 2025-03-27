from dataclasses import dataclass, field


@dataclass
class LoginSelectors:
    email_input: str = 'input[type="text"]'
    password_input: str = 'input[type="password"]'
    confirm_checkbox: str = 'div[class="ds-checkbox ds-checkbox--none ds-checkbox--bordered"]'
    login_button: str = 'div[role="button"]'


@dataclass
class InteractionSelectors:
    textbox: str = 'textarea[class="_27c9245"]'
    send_options_parent: str = 'div[class="ec4f5d61"]'
    send_button: str = 'div[class="_6f28693"]'
    new_chat_button: str = 'div[class="_5a8ac7a"]'


@dataclass
class BackendSelectors:
    response_generating: str = 'div[class="_4f9bf79 d7dc56a8"]'
    response_generated: str = 'div[class="_4f9bf79 d7dc56a8 _43c05b5"]'


@dataclass
class DeepSeekSelectors:
    login: LoginSelectors = field(default_factory=LoginSelectors)
    interactions: InteractionSelectors = field(default_factory=InteractionSelectors)
    backend: BackendSelectors = field(default_factory=BackendSelectors)
