"""
Configuration for the plexe library.
"""

import importlib
import logging
import sys
import warnings
from dataclasses import dataclass, field
from functools import cached_property
from importlib.resources import files
from typing import List

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = files("aiden").joinpath("prompts")


# configure warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


def is_package_available(package_name: str) -> bool:
    """Check if a Python package is available/installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


@dataclass(frozen=True)
class _Config:
    @dataclass(frozen=True)
    class _FileStorageConfig:
        model_cache_dir: str = field(default=".smolcache/")
        model_dir: str = field(default="model_files/")

    @dataclass(frozen=True)
    class _LoggingConfig:
        level: str = field(default="INFO")
        format: str = field(default="[%(asctime)s - %(name)s - %(levelname)s - (%(threadName)-10s)]: - %(message)s")

    @dataclass(frozen=True)
    class _ExecutionConfig:
        runfile_name: str = field(default="execution_script.py")

    @dataclass(frozen=True)
    class _CodeGenerationConfig:
        # Base ML packages that are always available
        _base_packages: List[str] = field(
            default_factory=lambda: [
                "pandas",
                "numpy",
                "joblib",
                "mlxtend",
                "pyarrow",
            ]
        )

        # Deep learning packages that are optional
        _deep_learning_packages: List[str] = field(
            default_factory=lambda: [
                "dagster",
            ]
        )

        # Deep learning packages that are optional
        _dagster_packages: List[str] = field(
            default_factory=lambda: [
                "dagster",
            ]
        )

        # Additional standard library modules for agent execution
        _standard_lib_modules: List[str] = field(
            default_factory=lambda: [
                "pathlib",
                "typing",
                "dataclasses",
                "json",
                "io",
                "time",
                "datetime",
                "os",
                "sys",
                "math",
                "random",
                "itertools",
                "collections",
                "functools",
                "operator",
                "re",
                "copy",
                "warnings",
                "logging",
                "importlib",
                "types",
                "aiden",
            ]
        )

        @property
        def allowed_packages(self) -> List[str]:
            """Dynamically determine which packages are available and can be used."""
            available_packages = self._base_packages.copy()

            # Check if dagster packages are installed and add them if they are
            for package in self._dagster_packages:
                if is_package_available(package):
                    available_packages.append(package)

            return available_packages

        @property
        def authorized_agent_imports(self) -> List[str]:
            """Return the combined list of allowed packages and standard library modules for agent execution."""
            # Start with allowed packages
            imports = self.allowed_packages.copy()

            # Add standard library modules
            imports.extend(self._standard_lib_modules)

            return imports

        @property
        def dagster_available(self) -> bool:
            """Check if dagster packages are available."""
            return any(is_package_available(pkg) for pkg in self._dagster_packages)

    # configuration objects
    file_storage: _FileStorageConfig = field(default_factory=_FileStorageConfig)
    logging: _LoggingConfig = field(default_factory=_LoggingConfig)
    code_generation: _CodeGenerationConfig = field(default_factory=_CodeGenerationConfig)
    execution: _ExecutionConfig = field(default_factory=_ExecutionConfig)


@dataclass(frozen=True)
class _PromptTemplates:
    template_dir: str = field(default=TEMPLATE_DIR)

    @cached_property
    def env(self) -> Environment:
        return Environment(loader=FileSystemLoader(str(self.template_dir)))

    def _render(self, template_name: str, **kwargs) -> str:
        template = self.env.get_template(template_name)
        return template.render(**kwargs)

    def transformation_system(self) -> str:
        return self._render("code_generator/system_prompt.jinja")

    def transformation_generate(
        self, problem_statement, plan, history, input_datasets, output_dataset, allowed_packages, environment_type
    ) -> str:
        return self._render(
            "code_generator/generate.jinja",
            problem_statement=problem_statement,
            plan=plan,
            history=history,
            input_datasets=input_datasets,
            output_dataset=output_dataset,
            allowed_packages=allowed_packages,
            environment_type=environment_type,
        )

    def transformation_fix(
        self, transformation_code, plan, review, problems, allowed_packages, environment_type
    ) -> str:
        return self._render(
            "code_generator/fix.jinja",
            transformation_code=transformation_code,
            plan=plan,
            review=review,
            problems=problems,
            allowed_packages=allowed_packages,
            environment_type=environment_type,
        )

    def transformation_review(
        self, problem_statement, plan, transformation_code, problems, allowed_packages, environment_type
    ) -> str:
        return self._render(
            "code_generator/review.jinja",
            problem_statement=problem_statement,
            plan=plan,
            transformation_code=transformation_code,
            problems=problems,
            allowed_packages=allowed_packages,
            environment_type=environment_type,
        )

    def cot_system(self) -> str:
        return self._render("utils/system_prompt.jinja")

    def cot_summarize(self, context: str) -> str:
        return self._render("utils/cot_summarize.jinja", context=context)

    def agent_builder_prompt(
        self,
        intent: str,
        input_datasets: list[str] | None = None,
        output_dataset: str | None = None,
        working_dir: str | None = None,
    ) -> str:
        return self._render(
            "manager_prompt.jinja",
            intent=intent,
            input_datasets=input_datasets,
            output_dataset=output_dataset,
            working_dir=working_dir,
        )


# Instantiate configuration and templates
config: _Config = _Config()
# code_templates: _CodeTemplates = _CodeTemplates()
prompt_templates: _PromptTemplates = _PromptTemplates()


# Default logging configuration
def configure_logging(level: str | int = logging.INFO, file: str | None = None) -> None:
    # Configure the library's root logger
    sm_root_logger = logging.getLogger("aiden")
    sm_root_logger.setLevel(level)

    # Clear existing handlers to avoid duplicate logs
    sm_root_logger.handlers = []

    # Define a common formatter
    formatter = logging.Formatter(config.logging.format)

    stream_handler = logging.StreamHandler()
    # Only apply reconfigure if the stream supports it
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    stream_handler.setFormatter(formatter)
    sm_root_logger.addHandler(stream_handler)

    if file:
        file_handler = logging.FileHandler(file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        sm_root_logger.addHandler(file_handler)


configure_logging(level=config.logging.level)
