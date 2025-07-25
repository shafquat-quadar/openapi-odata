import argparse
import os
import requests

from config import settings


def main():
    parser = argparse.ArgumentParser(description="Download OData service metadata")
    parser.add_argument("service", help="Name of the OData service")
    parser.add_argument(
        "--base-url",
        default=settings.base_url or "http://example.com",
        help="Base URL of the OData system",
    )
    parser.add_argument(
        "--output",
        default="sample_metadata.xml",
        help="Path to save the downloaded XML",
    )
    parser.add_argument(
        "--username",
        default=settings.user or "user",
        help="Basic auth username",
    )
    parser.add_argument(
        "--password",
        default=settings.password or "password",
        help="Basic auth password",
    )
    args = parser.parse_args()

    url = f"{args.base_url.rstrip('/')}/{args.service.strip('/')}/$metadata"
    resp = requests.get(url, auth=(args.username, args.password))
    resp.raise_for_status()
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(resp.text)
    print(f"Metadata saved to {args.output}")


if __name__ == "__main__":
    main()
