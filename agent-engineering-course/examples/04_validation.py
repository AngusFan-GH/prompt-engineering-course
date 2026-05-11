"""
输出质量控制与验证系统
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum
from datetime import datetime
import re
import json


class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"


@dataclass
class ValidationResult:
    """验证结果"""
    status: ValidationStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_valid(self) -> bool:
        return self.status in [ValidationStatus.PASSED, ValidationStatus.WARNING]


class OutputValidator:
    """
    输出验证器基类
    
    各种验证规则:
    - 格式验证 (JSON/列表/字数限制)
    - 内容验证 (关键词/正则)
    - 语义验证 (使用LLM判断)
    - 业务规则验证
    """
    
    def validate(self, output: Any) -> ValidationResult:
        raise NotImplementedError


class JSONFormatValidator(OutputValidator):
    """JSON格式验证器"""
    
    def __init__(self, required_keys: List[str] = None):
        self.required_keys = required_keys or []
    
    def validate(self, output: Any) -> ValidationResult:
        if isinstance(output, str):
            try:
                data = json.loads(output)
            except json.JSONDecodeError as e:
                return ValidationResult(
                    ValidationStatus.FAILED,
                    f"Invalid JSON format: {e}",
                    {"error": str(e)}
                )
        elif isinstance(output, dict):
            data = output
        else:
            return ValidationResult(
                ValidationStatus.FAILED,
                f"Expected dict or JSON string, got {type(output)}"
            )
        
        # 检查必需键
        missing_keys = [k for k in self.required_keys if k not in data]
        if missing_keys:
            return ValidationResult(
                ValidationStatus.FAILED,
                f"Missing required keys: {missing_keys}",
                {"missing_keys": missing_keys}
            )
        
        return ValidationResult(ValidationStatus.PASSED, "Valid JSON with all required keys")


class LengthValidator(OutputValidator):
    """长度验证器"""
    
    def __init__(self, min_length: int = None, max_length: int = None):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, output: Any) -> ValidationResult:
        text = str(output) if not isinstance(output, str) else output
        length = len(text)
        
        issues = []
        if self.min_length and length < self.min_length:
            issues.append(f"Too short: {length} < {self.min_length}")
        if self.max_length and length > self.max_length:
            issues.append(f"Too long: {length} > {self.max_length}")
        
        if issues:
            return ValidationResult(
                ValidationStatus.FAILED,
                "; ".join(issues),
                {"length": length}
            )
        
        return ValidationResult(
            ValidationStatus.PASSED,
            f"Length OK: {length}",
            {"length": length}
        )


class KeywordValidator(OutputValidator):
    """关键词验证器"""
    
    def __init__(self, required_keywords: List[str] = None, 
                 forbidden_keywords: List[str] = None,
                 case_sensitive: bool = False):
        self.required_keywords = required_keywords or []
        self.forbidden_keywords = forbidden_keywords or []
        self.case_sensitive = case_sensitive
    
    def validate(self, output: Any) -> ValidationResult:
        text = str(output)
        if not self.case_sensitive:
            text = text.lower()
        
        # 检查必需关键词
        missing = []
        for kw in self.required_keywords:
            check_kw = kw if self.case_sensitive else kw.lower()
            if check_kw not in text:
                missing.append(kw)
        
        # 检查禁用关键词
        found_forbidden = []
        for kw in self.forbidden_keywords:
            check_kw = kw if self.case_sensitive else kw.lower()
            if check_kw in text:
                found_forbidden.append(kw)
        
        issues = []
        if missing:
            issues.append(f"Missing keywords: {missing}")
        if found_forbidden:
            issues.append(f"Contains forbidden keywords: {found_forbidden}")
        
        if issues:
            return ValidationResult(
                ValidationStatus.FAILED,
                "; ".join(issues)
            )
        
        return ValidationResult(ValidationStatus.PASSED, "All keyword checks passed")


class RegexValidator(OutputValidator):
    """正则表达式验证器"""
    
    def __init__(self, pattern: str, error_message: str = "Pattern not matched"):
        self.pattern = re.compile(pattern)
        self.error_message = error_message
    
    def validate(self, output: Any) -> ValidationResult:
        text = str(output)
        match = self.pattern.search(text)
        
        if not match:
            return ValidationResult(
                ValidationStatus.FAILED,
                self.error_message,
                {"pattern": self.pattern.pattern}
            )
        
        return ValidationResult(
            ValidationStatus.PASSED,
            f"Pattern matched: {match.group()}",
            {"match": match.group()}
        )


class ValidationChain:
    """
    验证链
    
    组合多个验证器，短路或全部执行
    """
    
    def __init__(self, mode: str = "all"):
        """
        Args:
            mode: "all" 执行所有验证器
                  "any" 遇到第一个失败就停止
        """
        self.validators: List[OutputValidator] = []
        self.mode = mode
    
    def add(self, validator: OutputValidator) -> "ValidationChain":
        self.validators.append(validator)
        return self
    
    def validate(self, output: Any) -> List[ValidationResult]:
        results = []
        
        for validator in self.validators:
            result = validator.validate(output)
            results.append(result)
            
            if self.mode == "any" and not result.is_valid():
                break
        
        return results
    
    def validate_and_report(self, output: Any) -> bool:
        """验证并报告结果"""
        results = self.validate(output)
        
        print("\n=== 验证报告 ===")
        all_passed = True
        for result in results:
            status_icon = "✓" if result.is_valid() else "✗"
            print(f"{status_icon} [{result.status.value}] {result.message}")
            if not result.is_valid():
                all_passed = False
        
        return all_passed


# LLM辅助验证器
class LLMAssistedValidator(OutputValidator):
    """
    LLM辅助验证器
    
    使用LLM来判断输出是否符合要求
    适用于难以用规则验证的语义质量检查
    """
    
    def __init__(self, llm_client: Callable, criteria: str):
        """
        Args:
            llm_client: LLM调用函数
            criteria: 验证标准描述
        """
        self.llm_client = llm_client
        self.criteria = criteria
    
    def validate(self, output: Any) -> ValidationResult:
        prompt = f"""你是一个输出质量审核员。

验证内容:
{output}

验证标准:
{self.criteria}

请判断输出是否符合标准，只回答"通过"或"不通过"，并简述原因。
"""
        
        try:
            response = self.llm_client(prompt)
            
            if "通过" in response and "不通过" not in response:
                return ValidationResult(
                    ValidationStatus.PASSED,
                    "LLM validation passed",
                    {"llm_response": response}
                )
            else:
                return ValidationResult(
                    ValidationStatus.FAILED,
                    "LLM validation failed",
                    {"llm_response": response}
                )
        except Exception as e:
            return ValidationResult(
                ValidationStatus.WARNING,
                f"LLM validation error: {e}"
            )


# 验证器演示
def demo_validators():
    """验证器演示"""
    
    print("=== 验证器演示 ===\n")
    
    # 测试数据
    good_output = '{"name": "张三", "age": 25, "city": "北京"}'
    bad_output = '{"name": "张三"}'  # 缺少必需字段
    short_output = "Hi"
    
    # 创建验证链
    chain = ValidationChain(mode="all")
    chain.add(JSONFormatValidator(required_keys=["name", "age", "city"]))
    chain.add(LengthValidator(min_length=10, max_length=500))
    chain.add(KeywordValidator(
        required_keywords=["北京"],
        forbidden_keywords=["错误", "失败"]
    ))
    
    print("1. 测试有效输出:")
    chain.validate_and_report(good_output)
    
    print("\n2. 测试无效JSON:")
    chain.validate_and_report(bad_output)
    
    print("\n3. 测试过短内容:")
    chain.validate_and_report(short_output)
    
    # 测试正则验证器
    print("\n4. 测试正则验证器:")
    email_validator = RegexValidator(
        r'^[\w\.-]+@[\w\.-]+\.\w+$',
        "Invalid email format"
    )
    email_validator.validate("user@example.com")
    chain2 = ValidationChain()
    chain2.add(email_validator)
    chain2.validate_and_report("user@example.com")
    chain2.validate_and_report("invalid-email")


if __name__ == "__main__":
    demo_validators()
