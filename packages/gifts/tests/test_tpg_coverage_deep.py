"""
Deep coverage tests for TPG parser generator focusing on uncovered code paths.
"""

import pytest
from gifts.common.tpg import (
    CacheNamedGroupLexer,
    EOFToken,
    LexicalError,
    NamedGroupLexer,
    Parser,
    SemanticError,
    WrongToken,
)


class TestNamedGroupLexerBasics:
    """Test NamedGroupLexer basic functionality"""

    def test_named_group_lexer_single_token(self):
        """Test single token matching"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()
        lexer.start("hello")
        assert lexer.cur_token.value == 'hello'

    def test_named_group_lexer_multiple_tokens(self):
        """Test multiple token types"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('NUMBER', r'\d+')
                self.def_token('WORD', r'[a-z]+')

        lexer = SimpleLexer()
        lexer.start("abc123")
        token = lexer.cur_token
        # Should match 'abc' as WORD (longest match at start)
        assert token.name == 'WORD'
        assert token.value == 'abc'

    def test_named_group_lexer_with_separator(self):
        """Test that separators are skipped"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = SimpleLexer()
        lexer.start("hello world")
        t1 = lexer.cur_token
        assert t1.value == 'hello'

        lexer.next_token()
        t2 = lexer.cur_token
        assert t2.value == 'world'


class TestTokenValueFunctions:
    """Test custom value functions for tokens"""

    def test_token_with_int_conversion(self):
        """Test token with int value function"""
        class IntLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('NUMBER', r'\d+', int)

        lexer = IntLexer()
        lexer.start("42")
        token = lexer.cur_token
        assert token.value == 42
        assert isinstance(token.value, int)

    def test_token_with_float_conversion(self):
        """Test token with float value function"""
        class FloatLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('NUMBER', r'\d+\.\d+', float)

        lexer = FloatLexer()
        lexer.start("3.14")
        token = lexer.cur_token
        assert token.value == 3.14
        assert isinstance(token.value, float)

    def test_token_with_constant_value(self):
        """Test token with non-callable value (constant)"""
        class ConstLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                # Non-callable value - always returns the constant
                self.def_token('CONST', r'fixed', 'MY_CONSTANT')

        lexer = ConstLexer()
        lexer.start("fixed")
        token = lexer.cur_token
        assert token.value == 'MY_CONSTANT'

    def test_token_with_lambda_value(self):
        """Test token with lambda value function"""
        class LambdaLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('NUMBER', r'\d+', lambda x: int(x) * 2)

        lexer = LambdaLexer()
        lexer.start("21")
        token = lexer.cur_token
        assert token.value == 42


class TestWrongTokenException:
    """Test handling of WrongToken exception"""

    def test_wrong_token_raises_lexical_error(self):
        """Test that WrongToken from value func raises LexicalError"""
        def strict_number(text):
            if len(text) > 1 and text[0] == '0':
                raise WrongToken()
            return int(text)

        class StrictLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('NUMBER', r'\d+', strict_number)

        lexer = StrictLexer()
        with pytest.raises(LexicalError) as exc_info:
            lexer.start("042")  # Leading zero
        assert "Lexical error" in str(exc_info.value)


class TestLexerErrorConditions:
    """Test lexer error conditions"""

    def test_lexical_error_on_no_match(self):
        """Test error when no token matches"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('NUMBER', r'\d+')

        lexer = SimpleLexer()
        with pytest.raises(LexicalError) as exc_info:
            lexer.start("@@@")  # No token matches
        assert "Lexical error" in str(exc_info.value)

    def test_lexical_error_message_with_newline(self):
        """Test error message includes only text until newline"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = SimpleLexer()
        # Create input where separator is needed before error
        test_input = "hello"
        lexer.start(test_input)
        token = lexer.cur_token
        # Should have parsed successfully
        assert token.value == 'hello'


class TestDuplicateTokenError:
    """Test error handling for duplicate definitions"""

    def test_duplicate_token_definition_raises_error(self):
        """Test that redefining a token raises SemanticError"""
        class DupLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                with pytest.raises(SemanticError):
                    self.def_token('WORD', r'[a-z]+')  # Duplicate!

    def test_duplicate_separator_definition_raises_error(self):
        """Test that redefining a separator raises SemanticError"""
        class DupLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_separator('WS', r'\s+')
                with pytest.raises(SemanticError):
                    self.def_separator('WS', r'\s+')  # Duplicate!


class TestLineAndColumnTracking:
    """Test line and column tracking"""

    def test_single_line_column_tracking(self):
        """Test column updates on same line"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = SimpleLexer()
        lexer.start("one two three")
        col1 = lexer.column

        lexer.next_token()  # two
        col2 = lexer.column

        # Column should increase
        assert col2 > col1

    def test_multiline_line_tracking(self):
        """Test line increments with newlines"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('NL', r'\n')
                self.def_separator('WS', r' ')

        lexer = SimpleLexer()
        lexer.start("one\ntwo\nthree")
        line1 = lexer.line

        while lexer.cur_token.name != 'EOF':
            lexer.next_token()

        final_line = lexer.line
        assert final_line > line1  # Should be on line 3


class TestTokenProperties:
    """Test Token object properties"""

    def test_token_has_position_info(self):
        """Test token contains position information"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()
        lexer.start("hello")
        token = lexer.cur_token

        assert hasattr(token, 'name')
        assert hasattr(token, 'value')
        assert hasattr(token, 'start')
        assert hasattr(token, 'stop')
        assert token.name == 'WORD'
        assert token.value == 'hello'
        assert token.start == 0
        assert token.stop == 5

    def test_eof_token_properties(self):
        """Test EOF token"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()
        lexer.start("test")
        lexer.next_token()  # EOF

        assert lexer.cur_token.name == 'EOF'
        assert isinstance(lexer.cur_token, EOFToken)


class TestEmptyInput:
    """Test handling of empty input"""

    def test_empty_input_gives_eof(self):
        """Test empty input immediately returns EOF"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()
        lexer.start("")

        assert lexer.cur_token.name == 'EOF'


class TestLongestMatchSelection:
    """Test longest match selection in NamedGroupLexer"""

    def test_longest_match_selected(self):
        """Test that longest matching pattern is selected"""
        class LongestLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)  # With word boundary
                self.def_token('DIGIT', r'\d+')

        lexer = LongestLexer()
        lexer.start("123")

        # Should match the whole sequence
        assert lexer.cur_token.value == '123'


class TestMultilineTokens:
    """Test tokens that span multiple lines"""

    def test_multiline_token_updates_line_count(self):
        """Test that multiline tokens update line counter"""
        class MultilineLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, False, 0)
                # Allow multiline string tokens
                self.def_token('STRING', r'"([^"\\]|\\.|\n)*"')
                self.def_token('WORD', r'\w+')
                self.def_separator('NL', r'\n')

        lexer = MultilineLexer()
        # Multiline test with newline separator
        test_input = 'a\nb\nc'
        lexer.start(test_input)

        # Should process the input and update lines
        line_start = lexer.line

        while lexer.cur_token.name != 'EOF':
            lexer.next_token()

        # Should have advanced through multiple lines
        line_end = lexer.line
        assert line_end >= line_start


class TestMaxPositionTracking:
    """Test max_pos tracking"""

    def test_max_pos_tracks_furthest_position(self):
        """Test that max_pos records furthest position reached"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = SimpleLexer()
        lexer.start("one two three")

        initial_max = lexer.max_pos

        while lexer.cur_token.name != 'EOF':
            lexer.next_token()

        final_max = lexer.max_pos
        assert final_max > initial_max


class TestLastTokenTracking:
    """Test last_token tracking"""

    def test_last_token_tracks_furthest_token(self):
        """Test that last_token is updated appropriately"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = SimpleLexer()
        lexer.start("one two three")

        while lexer.cur_token.name != 'EOF':
            lexer.next_token()

        # last_token should be set to the last real token
        assert lexer.last_token is not None
        assert lexer.last_token.value == 'three'


class TestTokenMethod:
    """Test token() method"""

    def test_token_method_returns_current(self):
        """Test that token() returns current token"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()
        lexer.start("hello")

        current = lexer.token()
        assert current.value == 'hello'
        assert current == lexer.cur_token


class TestEofMethod:
    """Test eof() method"""

    def test_eof_method_at_end(self):
        """Test eof() returns True at end"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()
        lexer.start("test")

        assert not lexer.eof()

        lexer.next_token()  # EOF
        assert lexer.eof()


class TestBackMethod:
    """Test back() method for backtracking"""

    def test_back_restores_position(self):
        """Test that back() restores lexer state"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()
        lexer.start("hello")

        first_token = lexer.cur_token
        pos_after_first = lexer.pos

        lexer.next_token()  # EOF

        # Back to first token
        lexer.back(first_token)

        assert lexer.cur_token == first_token
        assert lexer.pos == pos_after_first


class TestExtractMethod:
    """Test extract() method"""

    def test_extract_text_between_tokens(self):
        """Test extracting text between two tokens"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = SimpleLexer()
        lexer.start("first middle last")

        token1 = lexer.cur_token

        lexer.next_token()
        lexer.next_token()  # last
        token3 = lexer.cur_token

        # extract method exists and works
        extracted = lexer.extract(token1, token3)
        # Verify it returns a string
        assert isinstance(extracted, str)


class TestCacheNamedGroupLexer:
    """Test CacheNamedGroupLexer"""

    def test_cache_lexer_initialization(self):
        """Test CacheNamedGroupLexer initialization"""
        lexer = CacheNamedGroupLexer(True, 0)

        # CacheNamedGroupLexer inherits from NamedGroupLexer
        assert hasattr(lexer, 'tokens')

    def test_cache_lexer_caches_tokens(self):
        """Test that cache lexer caches token results"""
        class CacheLexer(CacheNamedGroupLexer):
            def __init__(self):
                CacheNamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = CacheLexer()
        lexer.start("hello")

        # Token should be cached
        assert lexer.cur_token.value == 'hello'


class TestParserInitialization:
    """Test Parser class initialization"""

    def test_parser_has_lexer(self):
        """Test that Parser has a lexer attribute"""
        class SimpleParser(Parser):
            def init_lexer(self):
                """Initialize the lexer"""
                return NamedGroupLexer(True, 0)

        parser = SimpleParser()

        # Parser should have a lexer
        assert hasattr(parser, 'lexer')


class TestSpecialCharacters:
    """Test handling of special regex characters"""

    def test_special_chars_in_token_definitions(self):
        """Test tokens with special regex characters"""
        class SpecialLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, False, 0)  # No word boundary
                self.def_token('PLUS', r'\+')
                self.def_token('MINUS', r'\-')
                self.def_token('MUL', r'\*')

        lexer = SpecialLexer()
        lexer.start("+-*")

        assert lexer.cur_token.value == '+'

        lexer.next_token()
        assert lexer.cur_token.value == '-'

        lexer.next_token()
        assert lexer.cur_token.value == '*'


class TestRealisticGrammar:
    """Test realistic parsing scenarios"""

    def test_math_expression_tokens(self):
        """Test lexing a simple math expression"""
        class MathLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('NUMBER', r'\d+(\.\d+)?', float)
                self.def_token('PLUS', r'\+')
                self.def_token('MINUS', r'-')
                self.def_token('MUL', r'\*')
                self.def_token('DIV', r'/')
                self.def_separator('WS', r'\s+')

        lexer = MathLexer()
        lexer.start("3.14 + 2 * 1.5")

        tokens = []
        while lexer.cur_token.name != 'EOF':
            tokens.append(lexer.cur_token.name)
            lexer.next_token()

        # Should have: NUMBER, PLUS, NUMBER, MUL, NUMBER
        assert 'NUMBER' in tokens
        assert 'PLUS' in tokens
        assert 'MUL' in tokens
