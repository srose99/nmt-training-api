__version__ = '1.0.2'

import json
from dataclasses import dataclass
from enum import Enum
from string import Template
from typing import TypeVar

import delegator
from cleantext import clean

DEFAULT_DELIMITER = "NL_CMD"

Data = TypeVar("Data")


class ResponseFormat(Enum):
    JSON = "JSON"
    STRING = "STRING"


class CommandType(Enum):
    docker = "docker"
    docker_compose = "docker-compose"


@dataclass
class DockerResponse:
    command: str
    status: str
    type: ResponseFormat
    data: Data


_COMMANDS = {
    CommandType.docker: {
        1: {
            "type": ResponseFormat.JSON,
            "command": 'docker $command --format="{{json .}}"$delimiter'
        },
        2: {
            "type": ResponseFormat.STRING,
            "command": 'docker $command'
        }
    },
    CommandType.docker_compose: {
        1: {
            "type": ResponseFormat.STRING,
            "command": 'docker-compose $command'
        }
    }
}


def docker(command) -> DockerResponse:
    return _exe_and_parse(CommandType.docker, command)


def is_docker_set():
    return delegator.run("docker -v").return_code == 0


def is_docker_compose_set():
    return delegator.run("docker-compose -v").return_code == 0


def _parse_result(cmd_type: CommandType, command, format_type, response, return_code) -> DockerResponse:
    cmd = f"{cmd_type.value} {command}"
    status = 'SUCCESS' if return_code == 0 else 'FAILURE'
    frmt_type = format_type.value
    data = []
    if format_type == ResponseFormat.JSON:
        for x in response.split(DEFAULT_DELIMITER):
            if x and len(x) > 3:
                try:
                    data.append(json.loads(x))
                except ValueError:
                    data = _clean(response)
                    frmt_type = ResponseFormat.STRING.value
    else:
        data = [_clean(response)]
    return DockerResponse(command=cmd, status=status, type=frmt_type, data=data)


def docker_compose(command) -> DockerResponse:
    return _exe_and_parse(CommandType.docker_compose, command)


def _exe_and_parse(cmd_type, command) -> DockerResponse:
    format_type, return_code, response = _run(cmd_type, command, DEFAULT_DELIMITER)
    return _parse_result(cmd_type, command, format_type, response, return_code)


def _run(cmd_type: CommandType, command: str, formatter: str, exe_count: int = 1):
    command_tmpl = _COMMANDS[cmd_type][exe_count]
    cmd = delegator.run(Template(command_tmpl["command"]).substitute(command=command, delimiter=formatter))

    if cmd.return_code == 0:
        return command_tmpl["type"], 0, cmd.out

    if exe_count >= len(_COMMANDS[cmd_type]):
        return ResponseFormat.STRING, cmd.return_code, cmd.err

    return _run(cmd_type, command, formatter, exe_count + 1)


def _clean(response):
    return clean(response,
                 fix_unicode=True,
                 to_ascii=True,
                 lower=False,
                 no_line_breaks=False,
                 no_urls=False,
                 no_emails=False,
                 no_phone_numbers=False,
                 no_numbers=False,
                 no_digits=False,
                 no_currency_symbols=False,
                 no_punct=False,
                 replace_with_punct="",
                 lang="en"
                 )
