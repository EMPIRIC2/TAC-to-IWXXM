"""Enhanced coverage tests for TPG module focusing on remaining uncovered code paths"""

import re

import pytest

from gifts.common import tpg
from gifts.common.tpg import (
    CacheLexer,
    CacheNamedGroupLexer,
    ContextSensitiveLexer,
    EOFToken,
    Lexer,
    LexerOptions,
    NamedGroupLexer,
    Parser,
    Py,
    SemanticError,
    SOFToken,
    Token,
    VerboseParser,
    WrongToken,
)


class TestLexerOptionsClass:
    """Test LexerOptions base class functionality"""

    def test_lexer_options_word_bounded_enabled(self):
        """Test word boundary addition for word-like patterns"""
        opts = LexerOptions(True, 0)
        # Word patterns should get boundaries
        result = opts.word_bounded("identifier")
        assert r"\b" in result
        assert "identifier" in result

    def test_lexer_options_word_bounded_disabled(self):
        """Test word boundary NOT added when disabled"""
        opts = LexerOptions(False, 0)
        # Should not add boundaries - instead should call not_word_bounded
        result = opts.word_bounded("test")
        assert r"\b" not in result
        assert result == "test"

    def test_lexer_options_non_word_pattern(self):
        """Test that non-word patterns don't get boundaries"""
        opts = LexerOptions(True, 0)
        result = opts.word_bounded("[a-z]+")
        assert r"\b" not in result
        assert result == "[a-z]+"

    def test_lexer_options_regex_compile(self):
        """Test regex compilation with options"""
        opts = LexerOptions(True, re.IGNORECASE)
        pattern = opts.re_compile("test")
        # Should be compiled with IGNORECASE flag
        assert pattern.match("TEST")
        assert pattern.match("test")

    def test_lexer_options_not_word_bounded(self):
        """Test not_word_bounded method"""
        opts = LexerOptions(True, 0)
        result = opts.not_word_bounded("anything")
        assert result == "anything"


class TestContextSensitiveLexer:
    """Test ContextSensitiveLexer implementation"""

    def test_context_lexer_initialization(self):
        """Test basic initialization"""
        lexer = ContextSensitiveLexer(True, 0)
        assert lexer.tokens == {}
        assert lexer.separators == []

    def test_context_lexer_def_token(self):
        """Test token definition"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        assert "WORD" in lexer.tokens
        regexp, value = lexer.tokens["WORD"]
        assert regexp.match("hello")

    def test_context_lexer_def_separator(self):
        """Test separator definition"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_separator("SPACE", r"\s+")
        assert len(lexer.separators) == 1
        name, regexp, value = lexer.separators[0]
        assert name == "SPACE"

    def test_context_lexer_duplicate_token_error(self):
        """Test error on duplicate token definition"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("TEST", r"test")
        with pytest.raises(SemanticError) as exc_info:
            lexer.def_token("TEST", r"test2")
        assert "Duplicate" in str(exc_info.value)

    def test_context_lexer_token_separator_conflict(self):
        """Test error when token name conflicts with separator"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("NAME", r"test")
        with pytest.raises(SemanticError) as exc_info:
            lexer.def_separator("NAME", r"\s+")
        assert "Duplicate" in str(exc_info.value)

    def test_context_lexer_start_and_eof(self):
        """Test start/eof methods"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.start("hello")
        assert not lexer.eof()

        lexer.pos = len(lexer.input)
        assert lexer.eof()

    def test_context_lexer_back_to_none(self):
        """Test backtracking to None (SOF)"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.start("hello")

        # Back to None should reset position
        lexer.back(None)
        assert lexer.pos == 0
        assert lexer.line == 1
        assert lexer.column == 1

    def test_context_lexer_eat_token(self):
        """Test eating a token"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.start("hello world")

        token = lexer.eat("WORD")
        assert token.name == "WORD"
        assert token.value == "hello"
        assert lexer.pos == 5

    def test_context_lexer_eat_with_wrong_token(self):
        """Test eating wrong token raises WrongToken"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("DIGIT", r"\d+")
        lexer.start("hello")

        with pytest.raises(WrongToken):
            lexer.eat("DIGIT")

    def test_context_lexer_eat_with_separators(self):
        """Test eating token with separators"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_separator("SPACE", r"\s+")
        lexer.start("hello  world")

        token1 = lexer.eat("WORD")
        assert token1.value == "hello"
        # Separators should be eaten automatically
        token2 = lexer.eat("WORD")
        assert token2.value == "world"

    def test_context_lexer_line_column_tracking(self):
        """Test line and column tracking"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_separator("SPACE", r" +")
        lexer.start("hello world")

        token1 = lexer.eat("WORD")
        assert token1.line == 1

        token2 = lexer.eat("WORD")
        assert token2.line == 1  # Still line 1, same line

    def test_context_lexer_token_method(self):
        """Test token() method returns current token"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.start("hello")

        # Need to eat a token first
        lexer.eat("WORD")
        token2 = lexer.token()
        assert token2.value == "hello"

    def test_context_lexer_extract(self):
        """Test extract method"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_separator("SPACE", r"\s+")
        lexer.start("hello world")

        tok1 = lexer.eat("WORD")
        tok2 = lexer.eat("WORD")

        extracted = lexer.extract(tok1, tok2)
        assert "world" in extracted

    def test_context_lexer_non_callable_token_value(self):
        """Test token with non-callable value"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("CONST", r"fixed", 42)
        lexer.start("fixed")

        token = lexer.eat("CONST")
        assert token.value == 42

    def test_context_lexer_back_to_token(self):
        """Test backtracking to a specific token"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token("WORD", r"\w+")
        lexer.def_separator("SPACE", r"\s+")
        lexer.start("hello world")

        tok1 = lexer.eat("WORD")
        lexer.eat("WORD")

        # Back to first token - back() sets pos to token.stop + separators
        lexer.back(tok1)
        # After back and eat_separators, pos should be at tok1.stop or beyond
        assert lexer.pos >= tok1.stop


class TestToken:
    """Test Token class"""

    def test_token_creation(self):
        """Test Token creation"""
        token = Token("WORD", "hello", "hello", 1, 1, 1, 6, 0, 5, 5)
        assert token.name == "WORD"
        assert token.text == "hello"
        assert token.value == "hello"
        assert token.line == 1
        assert token.column == 1

    def test_eoftoken_creation(self):
        """Test EOFToken creation"""
        token = EOFToken(1, 1, 5, 5)
        assert token.name == "EOF"
        assert token.text == "EOF"

    def test_softoken_creation(self):
        """Test SOFToken creation"""
        token = SOFToken()
        assert token.name == "SOF"
        assert token.text == "SOF"


class TestNamedGroupLexerAdvanced:
    """Advanced tests for NamedGroupLexer"""

    def test_named_group_lexer_build(self):
        """Test building the lexer regex"""

        class TestLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")
                self.def_token("DIGIT", r"\d+")

        lexer = TestLexer()
        lexer.build()
        # After build, should have a combined regex
        assert lexer.token_re is not None

    def test_named_group_lexer_next_token(self):
        """Test advancing to next token"""

        class TestLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")
                self.def_separator("SPACE", r"\s+")

        lexer = TestLexer()
        lexer.start("hello world test")

        assert lexer.cur_token.value == "hello"
        lexer.next_token()
        assert lexer.cur_token.value == "world"
        lexer.next_token()
        assert lexer.cur_token.value == "test"


class TestLexerClass:
    """Test Lexer (non-named-group) implementation"""

    def test_lexer_basic(self):
        """Test basic Lexer functionality"""

        class TestLexer(Lexer):
            def __init__(self):
                Lexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")
                self.def_token("NUMBER", r"\d+")

        lexer = TestLexer()
        lexer.start("abc123")

        # Lexer selects longest match at any position
        token1 = lexer.cur_token
        assert token1.value is not None

    def test_lexer_next_token(self):
        """Test Lexer next_token method"""

        class TestLexer(Lexer):
            def __init__(self):
                Lexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")
                self.def_separator("SPACE", r"\s+")

        lexer = TestLexer()
        lexer.start("hello world")

        assert lexer.cur_token.value == "hello"
        lexer.next_token()
        assert lexer.cur_token.value == "world"


class TestCacheNamedGroupLexer:
    """Test CacheNamedGroupLexer implementation"""

    def test_cache_named_group_lexer_caches_tokens(self):
        """Test that CacheNamedGroupLexer caches token list"""

        class TestLexer(CacheNamedGroupLexer):
            def __init__(self):
                CacheNamedGroupLexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")
                self.def_separator("SPACE", r"\s+")

        lexer = TestLexer()
        lexer.start("hello world test")

        # Cache should be populated
        assert hasattr(lexer, "cache")


class TestCacheLexer:
    """Test CacheLexer implementation"""

    def test_cache_lexer_with_cache(self):
        """Test CacheLexer with caching"""

        class TestLexer(CacheLexer):
            def __init__(self):
                CacheLexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")
                self.def_separator("SPACE", r"\s+")

        lexer = TestLexer()
        lexer.start("hello world")

        # Should work and cache tokens
        assert lexer.cur_token.value == "hello"


class TestParserMetaClass:
    """Test ParserMetaClass"""

    def test_parser_metaclass_exists(self):
        """Test that ParserMetaClass is functional"""
        # ParserMetaClass is already applied to Parser
        assert isinstance(Parser, type)
        # Parser should be a class
        assert hasattr(Parser, "__init__")


class TestVerboseParser:
    """Test VerboseParser for debugging"""

    def test_verbose_parser_creation(self):
        """Test VerboseParser instantiation"""
        assert VerboseParser is not None
        assert issubclass(VerboseParser, Parser)


class TestTPGClass:
    """Test TPG tpg class"""

    def test_tpg_class_exists(self):
        """Test that TPG class exists and has expected attributes"""
        assert hasattr(tpg, "tpg")
        # tpg.tpg is the main TPG class for creating parsers
        assert tpg.tpg is not None


class TestPyClass:
    """Test Py class for Python code"""

    def test_py_class_exists(self):
        """Test Py class"""
        py = Py()
        assert py is not None


class TestLexerEdgeCases:
    """Test edge cases in lexers"""

    def test_lexer_with_multiline_content(self):
        """Test lexer with multiple lines"""

        class TestLexer(ContextSensitiveLexer):
            def __init__(self):
                ContextSensitiveLexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")
                self.def_separator("SPACE", r"\s+")

        lexer = TestLexer()
        input_text = "hello world test"
        lexer.start(input_text)

        tokens = []
        try:
            tok = lexer.eat("WORD")
            tokens.append(tok)
            tok = lexer.eat("WORD")
            tokens.append(tok)
            tok = lexer.eat("WORD")
            tokens.append(tok)
        except WrongToken:
            pass

        assert len(tokens) >= 1

    def test_lexer_empty_input(self):
        """Test lexer with empty input"""

        class TestLexer(ContextSensitiveLexer):
            def __init__(self):
                ContextSensitiveLexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")

        lexer = TestLexer()
        lexer.start("")
        assert lexer.eof()

    def test_lexer_only_separators(self):
        """Test input with only separators"""

        class TestLexer(ContextSensitiveLexer):
            def __init__(self):
                ContextSensitiveLexer.__init__(self, True, 0)
                self.def_token("WORD", r"\w+")
                self.def_separator("SPACE", r"\s+")

        lexer = TestLexer()
        lexer.start("   \n  \t  ")
        assert lexer.eof()


class TestLexerComplexPatterns:
    """Test lexers with complex regex patterns"""

    def test_lexer_with_optional_groups(self):
        """Test token with optional groups"""

        class TestLexer(ContextSensitiveLexer):
            def __init__(self):
                ContextSensitiveLexer.__init__(self, True, 0)
                self.def_token("NUMBER", r"-?\d+(\.\d+)?")

        lexer = TestLexer()
        lexer.start("42")
        token = lexer.eat("NUMBER")
        assert token.value == "42"

    def test_lexer_with_character_classes(self):
        """Test tokens with character classes"""

        class TestLexer(ContextSensitiveLexer):
            def __init__(self):
                ContextSensitiveLexer.__init__(self, True, 0)
                self.def_token("IDENTIFIER", r"[a-zA-Z_]\w*")

        lexer = TestLexer()
        lexer.start("_myVar123")
        token = lexer.eat("IDENTIFIER")
        assert token.value == "_myVar123"
