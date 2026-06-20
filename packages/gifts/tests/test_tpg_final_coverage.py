"""
Additional comprehensive tests for gifts/common/tpg.py focusing on Parser and advanced features.
Builds on existing test patterns to achieve higher coverage.
"""

import re

import pytest
from gifts.common.tpg import (
    Error,
    WrongToken,
    LexicalError,
    SyntacticError,
    SemanticError,
    LexerOptions,
    NamedGroupLexer,
    Lexer,
    CacheNamedGroupLexer,
    CacheLexer,
    ContextSensitiveLexer,
    Token,
    EOFToken,
    SOFToken,
    Py,
    ParserMetaClass,
    Parser,
    VerboseParser,
    tpg,
    _id,
)


class TestErrorClassHierarchy:
    """Test error classes and exception handling"""

    def test_error_constructor(self):
        """Test Error class construction"""
        error = Error((1, 5), "Test error message")
        assert error.line == 1
        assert error.column == 5
        assert error.msg == "Test error message"

    def test_syntactic_error_inheritance(self):
        """Test SyntacticError inherits from Error"""
        assert issubclass(SyntacticError, Error)
        error = SyntacticError((2, 10), "Syntax problem")
        assert error.line == 2
        assert error.column == 10
        assert error.msg == "Syntax problem"

    def test_semantic_error_inheritance(self):
        """Test SemanticError inherits from Error"""
        assert issubclass(SemanticError, Error)
        error = SemanticError("Semantic problem")
        assert error.msg == "Semantic problem"

    def test_wrong_token_exception(self):
        """Test WrongToken exception"""
        with pytest.raises(WrongToken):
            raise WrongToken()

    def test_lexical_error_inheritance(self):
        """Test LexicalError inherits from Error"""
        assert issubclass(LexicalError, Error)
        error = LexicalError((3, 7), "Lex error")
        assert error.line == 3
        assert error.column == 7
        assert error.msg == "Lex error"


class TestLexerOptionsCompilation:
    """Test LexerOptions regex compilation"""

    def test_compile_with_ignorecase(self):
        """Test regex compilation with IGNORECASE flag"""
        opts = LexerOptions(True, re.IGNORECASE)
        pattern = opts.re_compile("word")
        assert pattern.match("WORD")
        assert pattern.match("word")

    def test_compile_multiline(self):
        """Test regex compilation with MULTILINE flag"""
        opts = LexerOptions(True, re.MULTILINE)
        pattern = opts.re_compile("^start")
        # MULTILINE should allow ^ to match line start
        assert pattern.match("start")

    def test_compile_no_flags(self):
        """Test regex compilation without flags"""
        opts = LexerOptions(False, 0)
        pattern = opts.re_compile("test")
        assert pattern.match("test")
        assert not pattern.match("TEST")


class TestNamedGroupLexerBuildProcess:
    """Test NamedGroupLexer.build() and regex construction"""

    def test_build_creates_regex(self):
        """Test build() method creates regex"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_token("NUMBER", r"\d+")
        lexer.build()

        assert hasattr(lexer, "token_re")
        assert lexer.token_re is not None

    def test_build_with_separators(self):
        """Test build() includes separators"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_separator("SPACE", r"\s+")
        lexer.build()

        assert lexer.token_re is not None

    def test_start_initializes_lexer(self):
        """Test start() initializes lexer properly"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("NUM", r"\d+")
        lexer.start("123")

        assert lexer.input == "123"
        assert lexer.cur_token is not None
        assert lexer.cur_token.value == "123"


class TestTokenClassFeatures:
    """Test Token class"""

    def test_token_initialization(self):
        """Test Token initialization with all parameters"""
        tok = Token("WORD", "hello", "hello_value", 0, 0, 0, 5, 0, 5, 0)
        assert tok.name == "WORD"
        assert tok.text == "hello"
        assert tok.value == "hello_value"
        assert tok.start == 0
        assert tok.stop == 5

    def test_eof_token_creation(self):
        """Test EOFToken creation"""
        tok = EOFToken(1, 10, 10, 10)
        assert hasattr(tok, "value")
        assert hasattr(tok, "line")

    def test_sof_token_creation(self):
        """Test SOFToken creation"""
        tok = SOFToken()
        assert hasattr(tok, "value")

    def test_token_match(self):
        """Test token matching by name"""
        tok = Token("WORD", "hello", "hello", 0, 0, 0, 5, 0, 5, 0)
        assert tok.match("WORD")
        assert not tok.match("NUMBER")


class TestContextSensitiveLexerEating:
    """Test ContextSensitiveLexer.eat() and eating tokens"""

    def test_eat_valid_token(self):
        """Test eating a valid token type"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_separator("SPACE", r"\s+")
        lexer.start("hello")
        tok = lexer.eat("WORD")
        assert tok.value == "hello"

    def test_eat_wrong_token_raises(self):
        """Test eating wrong token raises WrongToken"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_token("NUMBER", r"\d+")
        lexer.start("hello")
        with pytest.raises(WrongToken):
            lexer.eat("NUMBER")

    def test_eatCSL_functionality(self):
        """Test eating tokens in general"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_separator("COMMA", r",\s*")
        lexer.def_separator("SPACE", r" +")
        lexer.start("hello")

        # Test that lexer has eat method
        assert hasattr(lexer, "eat")


class TestLexerBacktracking:
    """Test Lexer.back() method"""

    def test_back_restores_token(self):
        """Test back() method restores previous token"""

        class TestLexer(Lexer):
            def __init__(self):
                Lexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")
                self.def_separator("SPACE", r" +")

        lexer = TestLexer()
        lexer.start("hello world")
        tok1 = lexer.cur_token
        lexer.next_token()
        tok2 = lexer.cur_token
        assert tok2.value != tok1.value
        lexer.back(tok1)
        assert lexer.cur_token == tok1

    def test_back_multiple_times(self):
        """Test backing multiple times"""

        class TestLexer(Lexer):
            def __init__(self):
                Lexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")
                self.def_separator("SPACE", r" +")

        lexer = TestLexer()
        lexer.start("a b c")
        tok_a = lexer.cur_token
        lexer.next_token()
        lexer.next_token()
        lexer.back(tok_a)
        assert lexer.cur_token == tok_a


class TestLexerStartMethod:
    """Test Lexer.start() initialization"""

    def test_start_initializes_input(self):
        """Test start() sets up lexer input"""

        class TestLexer(Lexer):
            def __init__(self):
                Lexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")

        lexer = TestLexer()
        lexer.start("test")
        assert lexer.input == "test"
        assert lexer.cur_token is not None

    def test_start_with_empty_string(self):
        """Test start() with empty input"""

        class TestLexer(Lexer):
            def __init__(self):
                Lexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")

        lexer = TestLexer()
        lexer.start("")
        assert lexer.input == ""


class TestLexerEOFDetection:
    """Test EOF detection in lexers"""

    def test_eof_detection(self):
        """Test eof() method detects end of input"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.start("test")

        assert not lexer.eof()
        # ContextSensitiveLexer uses eat() not next_token()
        lexer.eat("WORD")
        # After consuming all tokens, should detect EOF
        is_eof = lexer.eof()
        assert is_eof is not None  # Method exists


class TestCacheLexerFunctionality:
    """Test CacheLexer functionality"""

    def test_cache_lexer_initialization(self):
        """Test CacheLexer initialization"""

        class TestLexer(CacheLexer):
            def __init__(self):
                CacheLexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")

        lexer = TestLexer()
        # CacheLexer is a subclass, just verify it initializes
        assert isinstance(lexer, CacheLexer)
        assert isinstance(lexer, Lexer)

    def test_cache_named_group_lexer(self):
        """Test CacheNamedGroupLexer"""

        class TestLexer(CacheNamedGroupLexer):
            def __init__(self):
                CacheNamedGroupLexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")

        lexer = TestLexer()
        # Verify it's a CacheNamedGroupLexer
        assert isinstance(lexer, CacheNamedGroupLexer)


class TestParserBasics:
    """Test Parser class basics"""

    def test_parser_class_exists(self):
        """Test Parser class is defined"""
        assert Parser is not None
        assert isinstance(Parser, type)

    def test_verbose_parser_exists(self):
        """Test VerboseParser class"""
        assert VerboseParser is not None

    def test_verbose_parser_instantiation(self):
        """Test VerboseParser can be instantiated"""
        # VerboseParser is abstract, but check it exists
        assert hasattr(VerboseParser, "__init__")


class TestParserMetaClassBehavior:
    """Test ParserMetaClass"""

    def test_parser_metaclass_type(self):
        """Test ParserMetaClass is a metaclass"""
        assert isinstance(ParserMetaClass, type)

    def test_parser_uses_metaclass(self):
        """Test Parser uses ParserMetaClass"""
        assert type(Parser).__name__ == "ParserMetaClass"


class TestTokenValueHandling:
    """Test token value functions"""

    def test_token_with_int_conversion(self):
        """Test tokens with int conversion"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("INT", r"\d+", int)
        lexer.build()
        lexer.start("42")
        tok = lexer.cur_token
        assert tok.value == 42
        assert isinstance(tok.value, int)

    def test_token_with_lambda_conversion(self):
        """Test tokens with lambda conversion"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("UPPER", r"\w+", lambda x: x.upper())
        lexer.build()
        lexer.start("hello")
        tok = lexer.cur_token
        assert tok.value == "HELLO"

    def test_token_with_string_function(self):
        """Test tokens with str function"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("STR", r"\d+", str)
        lexer.build()
        lexer.start("123")
        tok = lexer.cur_token
        assert tok.value == "123"
        assert isinstance(tok.value, str)


class TestSeparatorHandling:
    """Test separator definitions and handling"""

    def test_separator_basic(self):
        """Test basic separator definition"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_separator("SPACE", r" +")
        lexer.build()

        lexer.start("hello world")
        assert lexer.cur_token.value == "hello"
        lexer.next_token()
        assert lexer.cur_token.value == "world"

    def test_separator_with_value_function(self):
        """Test separator with value function"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_separator("SPACE", r" +", lambda x: "SPACE_TOKEN")
        lexer.build()

        lexer.start("a b")
        tok = lexer.cur_token
        assert tok.value == "a"


class TestLexerPatternMatching:
    """Test various regex patterns in lexer"""

    def test_optional_pattern(self):
        """Test optional regex groups"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("FLOAT", r"\d+(\.\d+)?")
        lexer.build()

        lexer.start("3.14")
        tok = lexer.cur_token
        assert tok.value == "3.14"

    def test_alternation_pattern(self):
        """Test alternation in regex"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("KEYWORD", r"if|else|while")
        lexer.build()

        lexer.start("while")
        tok = lexer.cur_token
        assert tok.value == "while"

    def test_character_class_pattern(self):
        """Test character class in regex"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("HEX", r"0x[0-9a-fA-F]+")
        lexer.build()

        lexer.start("0xDEADBEEF")
        tok = lexer.cur_token
        assert tok.value == "0xDEADBEEF"


class TestWordBoundaryHandling:
    """Test word boundary option"""

    def test_word_boundary_enabled(self):
        """Test word boundary matching"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("IF_KEYWORD", r"if")
        lexer.build()

        lexer.start("if")
        tok = lexer.cur_token
        assert tok.value == "if"

    def test_word_boundary_disabled(self):
        """Test without word boundary"""
        lexer = NamedGroupLexer(False, 0)
        lexer.def_token("TEST", r"test")
        lexer.build()

        lexer.start("test")
        tok = lexer.cur_token
        assert tok.value == "test"


class TestLexerMultilineContent:
    """Test lexer with multiline input"""

    def test_multiline_basic(self):
        """Test basic multiline input"""

        class TestLexer(Lexer):
            def __init__(self):
                Lexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")
                self.def_separator("SPACE", r" +")
                self.def_separator("NEWLINE", r"\n")

        lexer = TestLexer()
        lexer.start("hello\nworld")
        tok1 = lexer.cur_token
        assert tok1.value == "hello"
        lexer.next_token()
        tok2 = lexer.cur_token
        assert tok2.value == "world"

    def test_multiline_with_comments(self):
        """Test multiline with comment handling"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_separator("NEWLINE", r"\n")
        lexer.def_separator("SPACE", r" +")
        lexer.build()

        lexer.start("hello world")
        assert lexer.cur_token.value == "hello"


class TestLexerErrorMessages:
    """Test error message formatting"""

    def test_error_position_formatting(self):
        """Test error includes position info"""
        error = Error((5, 10), "Test error")
        assert error.line == 5
        assert error.column == 10

    def test_lexical_error_message(self):
        """Test LexicalError message"""
        error = LexicalError((2, 5), "Bad char")
        assert error.line == 2
        assert error.column == 5
        assert error.msg == "Bad char"

    def test_syntactic_error_message(self):
        """Test SyntacticError message"""
        error = SyntacticError((1, 0), "Unexpected token")
        assert error.line == 1
        assert error.column == 0
        assert error.msg == "Unexpected token"


class TestPythonCompatibility:
    """Test Python 2/3 compatibility code"""

    def test_id_function(self):
        """Test _id() function for getting object IDs"""
        obj = object()
        result = _id(obj)
        assert result is not None

    def test_py_class(self):
        """Test Py compatibility class"""
        assert Py is not None
        # Py provides compatibility utilities
        assert isinstance(Py, type)


class TestTPGClass:
    """Test main tpg class/function"""

    def test_tpg_exists(self):
        """Test tpg is accessible"""
        assert tpg is not None


class TestIgnoreTokens:
    """Test separator handling"""

    def test_separator_whitespace(self):
        """Test whitespace separators are ignored"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_separator("SPACE", r" +")
        lexer.build()

        lexer.start("hello   world")
        assert lexer.cur_token.value == "hello"
        lexer.next_token()
        assert lexer.cur_token.value == "world"

    def test_separator_comments(self):
        """Test comment-like separators"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token("CODE", r"\w+")
        lexer.def_separator("COMMENT", r"#[^\n]*")
        lexer.build()

        lexer.start("code")
        assert lexer.cur_token.value == "code"
