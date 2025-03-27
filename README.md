**OpenSeek** is an open-source Python library that provides free access to DeepSeek models. Designed for developers and
researchers, it offers a simple and unified interface to interact with various DeepSeek LLM models without requiring API
keys, subscriptions, or paid plans.

## Installation

```cmd
pip install openseek
```

## Quick Start

### Asynchronous Usage

```python
import asyncio
from openseek import DeepSeek


async def main():
    async with DeepSeek(
            email="your_email@example.com",
            password="your_password",
            headless=True
    ) as api:
        response = await api.send_message("Расскажи мне о квантовой физике")
        print(response.text)


asyncio.run(main())
```

### Synchronous Usage

```python
from openseek import DeepSeek


def main():
    api = DeepSeek(
        email="your_email@example.com",
        password="your_password",
        headless=True
    )

    try:
        api.initialize_sync()
        response = api.send_message_sync("Расскажи мне о квантовой физике")
        print(response.text)
    finally:
        api.close_sync()


main()
```

## Features

- **Free Access**: Use DeepSeek models without API keys or paid subscriptions
- **Asynchronous and Synchronous API**: Flexibility for different usage scenarios
- **DeepThink Mode**: Activate advanced thinking features for more complex queries
- **Search Support**: Enable web search to get up-to-date information
- **Session Management**: Resume existing chats using a session ID

## Parameters

When initializing `DeepSeek`, the following parameters are available:

| Parameter         | Type             | Default | Description                             |
|-------------------|------------------|---------|-----------------------------------------|
| email             | str              | -       | Email for logging into DeepSeek         |
| password          | str              | -       | Password for logging into DeepSeek      |
| chat_id           | Optional\[str\]  | None    | ID of a specific chat session           |
| headless          | bool             | True    | Launch browser in headless mode         |
| verbose           | bool             | False   | Enable detailed logging                 |
| chrome_args       | Optional\[List\] | None    | Additional arguments for Chrome         |
| attempt_cf_bypass | bool             | True    | Attempt to bypass Cloudflare protection |

## Sending Messages

The `send_message` method accepts:

| Parameter       | Type  | Default | Description                                     |
|-----------------|-------|---------|-------------------------------------------------|
| message         | str   | -       | Message text to send                            |
| slow_mode       | bool  | False   | Send the message slowly, character by character |
| deepthink       | bool  | False   | Activate DeepThink feature                      |
| search          | bool  | False   | Activate search feature                         |
| timeout         | int   | 60      | Maximum response waiting time                   |
| slow_mode_delay | float | 0.25    | Delay between characters in slow\_mode          |

## Error Handling

The library can raise the following exceptions:

- `MissingCredentials`: Missing credentials (email or password)
- `InvalidCredentials`: Invalid credentials
- `ServerDown`: DeepSeek server is unavailable
- `MissingInitialization`: Required dependencies are missing or initialization not done

## Requirements

- Python 3.10 or higher
- Dependencies: beautifulsoup4, zendriver, inscriptis, pyvirtualdisplay (for Linux)

## License

MIT - see [LICENSE](LICENSE) for details.

## Author

Daniel Cuzneţov <danielcuznetov04@gmail.com>