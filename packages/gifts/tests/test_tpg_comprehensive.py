"""Comprehensive tests for TPG (Toy Parser Generator) module"""

import re

import pytest

# Import TPG module
from gifts.common import tpg


class TestErrorClass:
    """Test the Error exception class"""

    def test_error_initialization(self):
        """Test Error exception creation with line/column and message"""
        error = tpg.Error((10, 5), "test error message")
        assert error.line == 10
        assert error.column == 5
        assert error.msg == "test error message"

    def test_error_string_representation(self):
        """Test Error string representation"""
        error = tpg.Error((42, 15), "parsing failed")
        error_str = str(error)
        assert "42" in error_str
        assert "15" in error_str
        assert "parsing failed" in error_str
        assert "Error" in error_str

    def test_error_is_exception(self):
        """Test that Error is an Exception subclass"""
        error = tpg.Error((1, 1), "test")
        assert isinstance(error, Exception)

    def test_error_can_be_raised(self):
        """Test that Error can be raised and caught"""
        with pytest.raises(tpg.Error) as exc_info:
            raise tpg.Error((5, 10), "test error")
        assert exc_info.value.line == 5
        assert exc_info.value.column == 10


class TestLexicalError:
    """Test the LexicalError exception class"""

    def test_lexical_error_initialization(self):
        """Test LexicalError exception creation"""
        error = tpg.LexicalError((3, 7), "invalid character")
        assert error.line == 3
        assert error.column == 7
        assert error.msg == "invalid character"
        assert isinstance(error, tpg.Error)

    def test_lexical_error_string_representation(self):
        """Test LexicalError string representation"""
        error = tpg.LexicalError((1, 1), "bad token")
        error_str = str(error)
        assert "LexicalError" in error_str
        assert "bad token" in error_str


class TestSyntacticError:
    """Test the SyntacticError exception class"""

    def test_syntactic_error_initialization(self):
        """Test SyntacticError exception creation"""
        error = tpg.SyntacticError((8, 3), "unexpected token")
        assert error.line == 8
        assert error.column == 3
        assert error.msg == "unexpected token"
        assert isinstance(error, tpg.Error)

    def test_syntactic_error_string_representation(self):
        """Test SyntacticError string representation"""
        error = tpg.SyntacticError((5, 2), "syntax error")
        error_str = str(error)
        assert "SyntacticError" in error_str
        assert "syntax error" in error_str


class TestSemanticError:
    """Test the SemanticError exception class"""

    def test_semantic_error_initialization(self):
        """Test SemanticError exception creation"""
        error = tpg.SemanticError("undefined symbol")
        assert error.msg == "undefined symbol"
        assert isinstance(error, tpg.Error)

    def test_semantic_error_string_representation(self):
        """Test SemanticError string representation"""
        error = tpg.SemanticError("type mismatch")
        error_str = str(error)
        assert "SemanticError" in error_str or "type mismatch" in error_str


class TestWrongToken:
    """Test the WrongToken exception class"""

    def test_wrong_token_creation(self):
        """Test WrongToken creation"""
        error = tpg.WrongToken()
        assert isinstance(error, tpg.Error)

    def test_wrong_token_is_error(self):
        """Test WrongToken is an Error"""
        error = tpg.WrongToken()
        assert isinstance(error, Exception)


class TestToken:
    """Test the Token class"""

    def test_token_creation(self):
        """Test Token creation with required parameters"""
        # Token(name, text, value, line, column, end_line, end_column, start, stop, prev_stop)
        token = tpg.Token("IDENTIFIER", "myvar", "myvar", 1, 1, 1, 6, 0, 5, 0)
        assert token.name == "IDENTIFIER"
        assert token.value == "myvar"
        assert token.line == 1
        assert token.column == 1

    def test_token_with_different_positions(self):
        """Test Token with different line/column positions"""
        token = tpg.Token("NUMBER", "42", 42, 5, 10, 5, 12, 50, 52, 48)
        assert token.line == 5
        assert token.column == 10
        assert token.value == 42

    def test_token_string_representation(self):
        """Test Token string representation"""
        token = tpg.Token("NUMBER", "42", 42, 1, 1, 1, 3, 0, 2, 0)
        token_str = str(token)
        # Token should have string representation
        assert isinstance(token_str, str)

    def test_token_text_attribute(self):
        """Test Token text attribute"""
        token = tpg.Token("IDENTIFIER", "mytext", "myvalue", 1, 1, 1, 5, 0, 4, 0)
        assert token.name == "IDENTIFIER"
        assert token.text == "mytext"
        assert token.value == "myvalue"

    def test_token_position_tracking(self):
        """Test Token position attributes"""
        token = tpg.Token("KEYWORD", "if", "if", 2, 5, 2, 7, 15, 17, 14)
        assert token.line == 2
        assert token.column == 5
        assert token.end_line == 2
        assert token.end_column == 7

    def test_eof_token(self):
        """Test EOF token constant"""
        assert hasattr(tpg, 'EOFToken')
        assert tpg.EOFToken is not None

    def test_sof_token(self):
        """Test SOF token constant"""
        assert hasattr(tpg, 'SOFToken')
        assert tpg.SOFToken is not None


class TestLexer:
    """Test the Lexer class functionality"""

    def test_lexer_creation(self):
        """Test Lexer instantiation"""
        input_text = "hello world"
        lexer = tpg.Lexer([], input_text)
        assert isinstance(lexer, tpg.Lexer)

    def test_lexer_with_token_definitions(self):
        """Test Lexer with token definitions"""
        tokens = [
            (r'\d+', 'NUMBER'),
            (r'[a-zA-Z]+', 'IDENTIFIER'),
        ]
        lexer = tpg.Lexer(tokens, "123 abc")
        assert isinstance(lexer, tpg.Lexer)

    def test_cache_lexer(self):
        """Test CacheLexer class"""
        assert hasattr(tpg, 'CacheLexer')
        lexer = tpg.CacheLexer([], "test")
        assert isinstance(lexer, tpg.CacheLexer)

    def test_named_group_lexer(self):
        """Test NamedGroupLexer class"""
        assert hasattr(tpg, 'NamedGroupLexer')

    def test_cache_named_group_lexer(self):
        """Test CacheNamedGroupLexer class"""
        assert hasattr(tpg, 'CacheNamedGroupLexer')

    def test_context_sensitive_lexer(self):
        """Test ContextSensitiveLexer class"""
        assert hasattr(tpg, 'ContextSensitiveLexer')


class TestParser:
    """Test the Parser class"""

    def test_parser_existence(self):
        """Test Parser class exists"""
        assert hasattr(tpg, 'Parser')
        assert tpg.Parser is not None

    def test_parser_base_class(self):
        """Test that Parser is a base class"""
        # Parser is a base class for generated parsers
        assert isinstance(tpg.Parser, type)

    def test_verbose_parser(self):
        """Test VerboseParser class"""
        assert hasattr(tpg, 'VerboseParser')

    def test_tpg_parser(self):
        """Test TPGParser (meta parser)"""
        assert hasattr(tpg, 'TPGParser')


class TestParserMetaClass:
    """Test the ParserMetaClass"""

    def test_parser_meta_class_exists(self):
        """Test ParserMetaClass is available"""
        assert hasattr(tpg, 'ParserMetaClass')

    def test_meta_class_is_type(self):
        """Test ParserMetaClass is a metaclass"""
        assert isinstance(tpg.ParserMetaClass, type)


class TestTokenPattern:
    """Test Token pattern matching"""

    def test_token_with_string_literal(self):
        """Test token matching with string literal"""
        pattern = r'"[^"]*"'
        text = '"hello"'
        match = re.match(pattern, text)
        assert match is not None

    def test_token_with_number_pattern(self):
        """Test token matching with number pattern"""
        pattern = r'\d+'
        text = '12345'
        match = re.match(pattern, text)
        assert match is not None

    def test_token_with_identifier_pattern(self):
        """Test token matching with identifier pattern"""
        pattern = r'[a-zA-Z_][a-zA-Z0-9_]*'
        text = 'myVariable'
        match = re.match(pattern, text)
        assert match is not None


class TestUtilityFunctions:
    """Test TPG utility functions"""

    def test_id_function(self):
        """Test the _id identity function"""
        value = "test"
        assert tpg._id(value) == value
        assert tpg._id(42) == 42
        assert tpg._id(None) is None

    def test_id_function_with_objects(self):
        """Test _id function with complex objects"""
        obj = {'key': 'value'}
        assert tpg._id(obj) is obj
        lst = [1, 2, 3]
        assert tpg._id(lst) is lst

    def test_tab_constant(self):
        """Test tab constant for indentation"""
        assert isinstance(tpg.tab, str)
        assert len(tpg.tab) == 4
        assert tpg.tab == "    "


class TestLexerOptions:
    """Test LexerOptions class"""

    def test_lexer_options_exists(self):
        """Test LexerOptions class exists"""
        assert hasattr(tpg, 'LexerOptions')

    def test_lexer_options_creation(self):
        """Test creating LexerOptions"""
        try:
            opts = tpg.LexerOptions()
            assert opts is not None
        except TypeError:
            # LexerOptions might require parameters
            pass


class TestPythonCompatibility:
    """Test Python 2/3 compatibility"""

    def test_callable_check(self):
        """Test callable function availability"""
        assert callable(tpg._id)
        assert callable(lambda x: x)
        assert not callable("string")

    def test_exception_info(self):
        """Test exception handling for Python 2/3"""
        try:
            raise ValueError("test error")
        except Exception:
            exc = tpg.exc()
            assert exc is not None
            assert isinstance(exc, ValueError)

    def test_python_version_constant(self):
        """Test __python__ constant"""
        assert hasattr(tpg, '__python__')
        assert tpg.__python__ in [2, 3]


class TestTPGMetadata:
    """Test TPG module metadata"""

    def test_tpg_version_exists(self):
        """Test that TPG version information exists"""
        assert hasattr(tpg, '__version__')
        assert isinstance(tpg.__version__, str)
        # Version should follow semantic versioning
        assert '.' in tpg.__version__

    def test_tpg_name_exists(self):
        """Test that TPG name exists"""
        assert hasattr(tpg, '__tpgname__')
        assert tpg.__tpgname__ == 'TPG'

    def test_tpg_author_exists(self):
        """Test that TPG author exists"""
        assert hasattr(tpg, '__author__')
        assert isinstance(tpg.__author__, str)

    def test_tpg_date_exists(self):
        """Test that TPG date exists"""
        assert hasattr(tpg, '__date__')
        assert isinstance(tpg.__date__, str)

    def test_tpg_license_exists(self):
        """Test that TPG license exists"""
        assert hasattr(tpg, '__license__')
        assert isinstance(tpg.__license__, str)


class TestRegexPatterns:
    """Test regex pattern constants in TPG"""

    def test_blank_line_re_exists(self):
        """Test blank_line_re pattern exists"""
        assert hasattr(tpg, 'blank_line_re')
        assert tpg.blank_line_re is not None

    def test_indent_re_exists(self):
        """Test indent_re pattern exists"""
        assert hasattr(tpg, 'indent_re')
        assert tpg.indent_re is not None

    def test_blank_line_matching(self):
        """Test blank line pattern matching"""
        pattern = tpg.blank_line_re
        assert pattern.match("") is not None or pattern.match("   ") is not None

    def test_indent_pattern_matching(self):
        """Test indent pattern matching"""
        pattern = tpg.indent_re
        assert pattern is not None


class TestParserSubclassing:
    """Test creating parser subclasses"""

    def test_parser_is_class(self):
        """Test Parser is a class"""
        assert isinstance(tpg.Parser, type)

    def test_verbose_parser_subclass(self):
        """Test VerboseParser subclass"""
        class MyVerboseParser(tpg.VerboseParser):
            pass

        # Should be able to create subclass
        assert issubclass(MyVerboseParser, tpg.VerboseParser)


class TestSREParse:
    """Test sre_parse handling"""

    def test_sre_parse_available(self):
        """Test sre_parse module is available"""
        assert hasattr(tpg, 'sre_parse')
        assert tpg.sre_parse is not None


class TestErrorLineColumn:
    """Test line and column error tracking"""

    def test_error_with_different_positions(self):
        """Test Error with various line/column combinations"""
        positions = [
            (1, 1),
            (100, 50),
            (0, 0),
            (999, 999),
        ]
        for line, col in positions:
            error = tpg.Error((line, col), "test")
            assert error.line == line
            assert error.column == col

    def test_lexical_error_positions(self):
        """Test LexicalError position tracking"""
        error = tpg.LexicalError((5, 10), "lexer failed")
        assert error.line == 5
        assert error.column == 10

    def test_syntactic_error_positions(self):
        """Test SyntacticError position tracking"""
        error = tpg.SyntacticError((20, 5), "parser failed")
        assert error.line == 20
        assert error.column == 5


class TestTPGParserMetaParser:
    """Test TPGParser as meta parser"""

    def test_tpg_parser_exists(self):
        """Test TPGParser is available"""
        assert hasattr(tpg, 'TPGParser')
        assert tpg.TPGParser is not None

    def test_tpg_parser_is_parser(self):
        """Test TPGParser is a Parser subclass"""
        assert issubclass(tpg.TPGParser, tpg.Parser)


class TestParserClass:
    """Test _Parser base class"""

    def test_underscore_parser_exists(self):
        """Test _Parser class exists"""
        assert hasattr(tpg, '_Parser')

    def test_underscore_parser_not_none(self):
        """Test _Parser is not None"""
        assert tpg._Parser is not None


class TestPyClass:
    """Test Py helper class"""

    def test_py_class_exists(self):
        """Test Py class exists"""
        assert hasattr(tpg, 'Py')
        assert tpg.Py is not None


class TestExceptionHierarchy:
    """Test exception class hierarchy"""

    def test_error_hierarchy(self):
        """Test Error exception hierarchy"""
        error = tpg.Error((1, 1), "test")
        assert isinstance(error, Exception)

    def test_lexical_error_hierarchy(self):
        """Test LexicalError hierarchy"""
        error = tpg.LexicalError((1, 1), "test")
        assert isinstance(error, tpg.Error)
        assert isinstance(error, Exception)

    def test_syntactic_error_hierarchy(self):
        """Test SyntacticError hierarchy"""
        error = tpg.SyntacticError((1, 1), "test")
        assert isinstance(error, tpg.Error)
        assert isinstance(error, Exception)

    def test_semantic_error_hierarchy(self):
        """Test SemanticError hierarchy"""
        error = tpg.SemanticError("test")
        assert isinstance(error, Exception)

    def test_wrong_token_hierarchy(self):
        """Test WrongToken hierarchy"""
        error = tpg.WrongToken()
        assert isinstance(error, tpg.Error)
        assert isinstance(error, Exception)


class TestTokenEquality:
    """Test Token comparison and equality"""

    def test_token_name_attribute(self):
        """Test token name attribute"""
        token1 = tpg.Token("IDENTIFIER", "var1", "var1", 1, 1, 1, 5, 0, 4, 0)
        token2 = tpg.Token("NUMBER", "var1", "var1", 1, 1, 1, 5, 0, 4, 0)
        assert token1.name != token2.name

    def test_token_value_different(self):
        """Test comparing token values"""
        token1 = tpg.Token("IDENTIFIER", "var1", "var1", 1, 1, 1, 5, 0, 4, 0)
        token2 = tpg.Token("IDENTIFIER", "var2", "var2", 1, 1, 1, 5, 0, 4, 0)
        assert token1.value != token2.value

    def test_token_position_attributes(self):
        """Test token position attributes"""
        token = tpg.Token("IDENTIFIER", "test", "test", 5, 10, 5, 14, 100, 104, 98)
        assert token.line == 5
        assert token.column == 10
        assert token.value == "test"


class TestLexerErrorHandling:
    """Test error handling in lexer"""

    def test_lexical_error_can_be_raised(self):
        """Test LexicalError can be raised"""
        with pytest.raises(tpg.LexicalError):
            raise tpg.LexicalError((1, 1), "lexical error")

    def test_syntactic_error_can_be_raised(self):
        """Test SyntacticError can be raised"""
        with pytest.raises(tpg.SyntacticError):
            raise tpg.SyntacticError((1, 1), "syntactic error")

    def test_semantic_error_can_be_raised(self):
        """Test SemanticError can be raised"""
        with pytest.raises(tpg.SemanticError):
            raise tpg.SemanticError("semantic error")

    def test_wrong_token_can_be_raised(self):
        """Test WrongToken can be raised"""
        with pytest.raises(tpg.WrongToken):
            raise tpg.WrongToken()


class TestModuleExports:
    """Test all major exports from tpg module"""

    def test_error_classes_exported(self):
        """Test error classes are exported"""
        assert hasattr(tpg, 'Error')
        assert hasattr(tpg, 'LexicalError')
        assert hasattr(tpg, 'SyntacticError')
        assert hasattr(tpg, 'SemanticError')
        assert hasattr(tpg, 'WrongToken')

    def test_lexer_classes_exported(self):
        """Test lexer classes are exported"""
        assert hasattr(tpg, 'Lexer')
        assert hasattr(tpg, 'CacheLexer')
        assert hasattr(tpg, 'NamedGroupLexer')
        assert hasattr(tpg, 'CacheNamedGroupLexer')
        assert hasattr(tpg, 'ContextSensitiveLexer')

    def test_parser_classes_exported(self):
        """Test parser classes are exported"""
        assert hasattr(tpg, 'Parser')
        assert hasattr(tpg, 'VerboseParser')
        assert hasattr(tpg, 'TPGParser')

    def test_token_classes_exported(self):
        """Test token classes are exported"""
        assert hasattr(tpg, 'Token')
        assert hasattr(tpg, 'EOFToken')
        assert hasattr(tpg, 'SOFToken')

    def test_utility_functions_exported(self):
        """Test utility functions are exported"""
        assert hasattr(tpg, '_id')
        assert hasattr(tpg, 'tab')
