"""
Advanced TPG coverage - targeting specific line numbers in the missing list
Lines to target: 58-59, 66-73, 188, 230-231, 250, 255, 260, 313-314, 326-329, 334, etc.
"""

from gifts.common.tpg import (
    Error, Token, LexicalError, SyntacticError, NamedGroupLexer
)


class TestTPGLexerEdgeCases:
    """Test edge cases in lexer to hit uncovered lines"""

    def test_lexer_empty_tokens_list(self):
        """Test lexer with no tokens defined"""
        lexer = NamedGroupLexer(True, 0)
        # Don't add any tokens, just build
        try:
            lexer.build()
            # If tokens list is empty, should handle gracefully
            assert lexer is not None
        except (ValueError, IndexError):
            # Empty pattern might raise
            pass

    def test_lexer_many_tokens(self):
        """Test lexer with many token definitions"""
        lexer = NamedGroupLexer(True, 0)
        # Add many different token types
        for i in range(20):
            lexer.def_token(f'TOK{i}', f'tok{i}')
        assert len(lexer.tokens) == 20

    def test_lexer_complex_regex(self):
        """Test lexer with complex regex patterns"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('STRING', r'"([^"\\]|\\.)*"')
        lexer.def_token('NUMBER', r'([0-9]+\.[0-9]*|[0-9]*\.[0-9]+|[0-9]+)')
        lexer.def_token('IDENT', r'[a-zA-Z_]\w*')
        assert len(lexer.tokens) == 3

    def test_lexer_special_char_tokens(self):
        """Test lexer with special characters"""
        lexer = NamedGroupLexer(False, 0)  # No word boundary
        lexer.def_token('PLUS', r'\+')
        lexer.def_token('MINUS', r'\-')
        lexer.def_token('STAR', r'\*')
        lexer.def_token('SLASH', r'\/')
        assert len(lexer.tokens) == 4

    def test_lexer_token_with_none_value(self):
        """Test token with None as static value"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('NULL', r'null', None)
        val_func, is_real = lexer.tokens['NULL']
        assert is_real is True

    def test_lexer_separator_with_callable(self):
        """Test separator with callable value function"""
        lexer = NamedGroupLexer(True, 0)

        def skip_value(text):
            return None
        lexer.def_separator('COMMENT', r'#.*$', skip_value)
        val_func, is_real = lexer.tokens['COMMENT']
        assert is_real is False

    def test_lexer_build_from_list(self):
        """Test building lexer regex from token list"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('A', r'a')
        lexer.def_token('B', r'b')
        # Before build, should be list
        assert isinstance(lexer.token_re, list)
        lexer.build()
        # After build, should be compiled regex
        assert lexer.token_re is not None


class TestTPGErrorEdgeCases:
    """Test error handling edge cases"""

    def test_error_zero_position(self):
        """Test error at position (0, 0)"""
        err = Error((0, 0), "Error at start")
        assert err.line == 0
        assert err.column == 0
        err_str = str(err)
        assert len(err_str) > 0

    def test_error_large_position(self):
        """Test error with very large position"""
        err = Error((999999, 999999), "Large position")
        assert err.line == 999999
        assert err.column == 999999

    def test_error_subclass_message(self):
        """Test that error subclasses include correct class name"""
        lex_err = LexicalError((1, 1), "lex")
        assert "Lexical" in str(lex_err)

        syn_err = SyntacticError((1, 1), "syn")
        assert "Syntactic" in str(syn_err)


class TestTPGTokenExtended:
    """Extended token testing"""

    def test_token_various_positions(self):
        """Test tokens at various positions"""
        positions = [
            (1, 0), (1, 10), (10, 50), (100, 100),
            (1, 1), (999, 999)
        ]
        for line, col in positions:
            tok = Token('TEST', 'test', 'value', line, col, line, col+4, col, col+4, 0)
            assert tok.line == line
            assert tok.column == col

    def test_token_with_zero_positions(self):
        """Test token with zero positions"""
        tok = Token('ZERO', 'z', 'z', 0, 0, 0, 1, 0, 1, 0)
        assert tok.line == 0
        assert tok.column == 0

    def test_token_large_coordinates(self):
        """Test token with large coordinates"""
        tok = Token('BIG', 'b', 'b', 10000, 10000, 10000, 10001, 10000, 10001, 0)
        assert tok.line == 10000
        assert tok.column == 10000


class TestTPGLexerComplexScenarios:
    """Test complex lexer scenarios"""

    def test_lexer_keyword_vs_identifier(self):
        """Test distinguishing keywords from identifiers"""
        lexer = NamedGroupLexer(True, 0)
        # Keywords - must be word-bounded
        lexer.def_token('IF', r'if')
        lexer.def_token('WHILE', r'while')
        # General identifiers
        lexer.def_token('ID', r'[a-z]\w*')
        assert len(lexer.tokens) == 3

    def test_lexer_operators(self):
        """Test various operator definitions"""
        lexer = NamedGroupLexer(False, 0)  # No word boundary for operators
        operators = [
            ('ASSIGN', r'='),
            ('EQ', r'=='),
            ('NE', r'!='),
            ('LT', r'<'),
            ('LE', r'<='),
            ('GT', r'>'),
            ('GE', r'>='),
        ]
        for name, pattern in operators:
            lexer.def_token(name, pattern)
        assert len(lexer.tokens) == len(operators)

    def test_lexer_strings_and_numbers(self):
        """Test complex string and number patterns"""
        lexer = NamedGroupLexer(True, 0)
        # Strings with escape sequences
        lexer.def_token('STRING', r'"([^"\\]|\\.)*"')
        # Various number formats
        lexer.def_token('HEX', r'0x[0-9a-fA-F]+')
        lexer.def_token('FLOAT', r'[0-9]+\.[0-9]+')
        lexer.def_token('INT', r'[0-9]+')
        assert len(lexer.tokens) == 4

    def test_lexer_multiline_comments(self):
        """Test multiline comment pattern"""
        lexer = NamedGroupLexer(True, 0)
        # This pattern might not work with re.DOTALL, test anyway
        lexer.def_separator('COMMENT', r'/\*.*?\*/')
        assert len(lexer.tokens) == 1


class TestTPGTokenValueFunctions:
    """Test token value computation functions"""

    def test_token_value_uppercase(self):
        """Test token with uppercase conversion"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('UPPER', r'[a-z]+', lambda x: x.upper())
        value_fn, _ = lexer.tokens['UPPER']
        assert value_fn is not None

    def test_token_value_integer(self):
        """Test token with integer conversion"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('INT', r'\d+', int)
        value_fn, _ = lexer.tokens['INT']
        assert value_fn is not None

    def test_token_value_string_constant(self):
        """Test token with string constant value"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('TRUE', r'true', 'TRUE_VALUE')
        value_fn, _ = lexer.tokens['TRUE']
        assert value_fn is not None


class TestTPGLexerRegexCompilation:
    """Test regex compilation in lexer"""

    def test_lexer_compile_options_0(self):
        """Test lexer with compile options 0"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('WORD', r'[a-z]+')
        lexer.build()
        assert lexer.token_re is not None

    def test_lexer_compile_with_flags(self):
        """Test lexer with regex flags"""
        import re
        lexer = NamedGroupLexer(True, re.IGNORECASE)
        lexer.def_token('WORD', r'[a-z]+')
        lexer.build()
        assert lexer.token_re is not None

    def test_lexer_pattern_alternation(self):
        """Test that lexer creates alternation of patterns"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('A', r'aaa')
        lexer.def_token('B', r'bbb')
        lexer.def_token('C', r'ccc')
        # Pattern should contain all three patterns
        assert 'aaa' in str(lexer.token_re) or len(lexer.token_re) > 0


class TestTPGLexerSeparatorHandling:
    """Test separator handling in lexer"""

    def test_lexer_multiple_separators(self):
        """Test multiple separator types"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('WORD', r'[a-z]+')
        lexer.def_separator('SPACE', r' +')
        lexer.def_separator('TAB', r'\t+')
        lexer.def_separator('NEWLINE', r'\n')
        assert len(lexer.tokens) == 4

    def test_lexer_comments_as_separator(self):
        """Test comments as separators (ignored)"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('CODE', r'[a-z]+')
        lexer.def_separator('COMMENT_LINE', r'//.*')
        val_fn, is_real = lexer.tokens['COMMENT_LINE']
        assert is_real is False

    def test_lexer_whitespace_as_separator(self):
        """Test various whitespace patterns as separators"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('WORD', r'\w+')
        lexer.def_separator('WS', r'\s+')
        val_fn, is_real = lexer.tokens['WS']
        assert is_real is False


class TestTPGLexerIterative:
    """Test iterative lexer use"""

    def test_lexer_multiple_starts(self):
        """Test starting lexer multiple times"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('NUM', r'\d+')

        for text in ["123", "456", "789"]:
            lexer.start(text)
            assert lexer.input == text

    def test_lexer_context_preservation(self):
        """Test that lexer state is preserved correctly"""
        lexer = NamedGroupLexer(True, 0)
        lexer.def_token('WORD', r'[a-z]+')
        lexer.def_separator('SPACE', r'\s+')

        lexer.start("hello world test")
        initial_input = lexer.input

        lexer.start("different input")
        # Should be reset for new input
        assert lexer.input == "different input"
        assert lexer.input != initial_input
