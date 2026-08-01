import argparse
import sys
from app.cli.commands import create_module, list_modules, validate, doctor, init_cmd, start_cmd, status_cmd, scaffold


def main():
    parser = argparse.ArgumentParser(
        description="BizOS Enterprise AI Operating System CLI",
        prog="bizos"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 1. init
    subparsers.add_parser("init", help="Initialize BizOS project configuration and directory structure")

    # 2. doctor
    doctor_parser = subparsers.add_parser("doctor", help="Run diagnostic health check on BizOS platform environment")
    doctor_parser.add_argument("--strict", action="store_true", help="Exit with non-zero code if any check fails")

    # 3. start
    start_parser = subparsers.add_parser("start", help="Launch BizOS API gateway server")
    start_parser.add_argument("--host", default="0.0.0.0", help="Host address to bind (default: 0.0.0.0)")
    start_parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    start_parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")

    # 4. status
    status_parser = subparsers.add_parser("status", help="Inspect live runtime process and API gateway status")
    status_parser.add_argument("--url", default="http://localhost:8000/api/v1/system/liveness", help="Gateway health endpoint URL")

    # 5. create
    create_parser = subparsers.add_parser("create", help="Scaffold a new BizOS module, plugin, connector, agent, or memory-provider")
    create_parser.add_argument("type", choices=["module", "plugin", "connector", "agent", "memory-provider"], help="Type of extension to create")
    create_parser.add_argument("name", help="Name of the extension (e.g., airline, whatsapp, qdrant)")
    create_parser.add_argument("--force", action="store_true", help="Force overwrite existing extension files")

    # 6. Legacy compatibility commands
    create_mod_parser = subparsers.add_parser("create-module", help="Create a new BizOS module (legacy)")
    create_mod_parser.add_argument("name", help="Name of the module (e.g., airline)")
    create_mod_parser.add_argument("--reference", action="store_true", help="Apply a reference implementation")
    create_mod_parser.add_argument("--template", help="Template to inherit from (e.g., retail)")
    create_mod_parser.add_argument("--force", action="store_true", help="Force overwrite existing module")

    subparsers.add_parser("list-modules", help="List installed business modules")
    subparsers.add_parser("validate", help="Validate domain module code")

    args = parser.parse_args()

    if args.command == "init":
        init_cmd.run(args)
    elif args.command == "doctor":
        doctor.run(args)
    elif args.command == "start":
        start_cmd.run(args)
    elif args.command == "status":
        status_cmd.run(args)
    elif args.command == "create":
        scaffold.run(args)
    elif args.command == "create-module":
        create_module.run(args)
    elif args.command == "list-modules":
        list_modules.run(args)
    elif args.command == "validate":
        validate.run(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
