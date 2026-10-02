"""Illustrate inherited organization guardrails as explicit denies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceControlPolicy:
    explicit_denies: frozenset[str]


def can_perform(action: str, identity_allowed: set[str], guardrail: ServiceControlPolicy) -> bool:
    return action in identity_allowed and action not in guardrail.explicit_denies


def main() -> None:
    production = ServiceControlPolicy(
        explicit_denies=frozenset({"iam:CreateUser"}),
    )
    role_permissions = {"ec2:DescribeInstances", "ec2:RunInstances", "iam:CreateUser"}

    for action in sorted(role_permissions):
        result = can_perform(action, role_permissions, production)
        print(f"{action}: {'allowed' if result else 'denied by guardrail'}")
    assert can_perform("ec2:RunInstances", role_permissions, production)
    assert not can_perform("iam:CreateUser", role_permissions, production)
    assert not can_perform("s3:DeleteBucket", role_permissions, production)


if __name__ == "__main__":
    main()
