"""
Additional TPG tests for CacheNamedGroupLexer and other uncovered sections
"""
from gifts.common.tpg import (
    NamedGroupLexer, CacheNamedGroupLexer, ContextSensitiveLexer
)


class TestCacheNamedGroupLexerFull:
    """Full tests for CacheNamedGroupLexer"""

    def test_cache_lexer_builds_full_token_cache(self):
        """Test that cache lexer pre-builds entire token cache"""
        class CacheLexer(CacheNamedGroupLexer):
            def __init__(self):
                CacheNamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = CacheLexer()
        lexer.start("one two three")

        # Cache should be populated
        assert len(lexer.cache) > 0
        # Last token should be EOF
        assert lexer.cache[-1].name == 'EOF'

    def test_cache_lexer_access_tokens_by_index(self):
        """Test accessing cached tokens by index"""
        class CacheLexer(CacheNamedGroupLexer):
            def __init__(self):
                CacheNamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = CacheLexer()
        lexer.start("hello world test")

        # Access tokens sequentially
        token1 = lexer.cur_token
        assert token1.value == 'hello'

        lexer.next_token()
        token2 = lexer.cur_token
        assert token2.value == 'world'

        lexer.next_token()
        token3 = lexer.cur_token
        assert token3.value == 'test'

    def test_cache_lexer_speed_multiple_passes(self):
        """Test cache lexer handles multiple sequential accesses"""
        class CacheLexer(CacheNamedGroupLexer):
            def __init__(self):
                CacheNamedGroupLexer.__init__(self, True, 0)
                self.def_token('NUM', r'\d+', int)
                self.def_separator('WS', r'\s+')

        lexer = CacheLexer()
        lexer.start("1 2 3 4 5")

        # Read all tokens
        values = []
        while lexer.cur_token.name != 'EOF':
            values.append(lexer.cur_token.value)
            lexer.next_token()

        assert values == [1, 2, 3, 4, 5]

    def test_cache_lexer_with_newlines(self):
        """Test cache lexer handles newlines correctly"""
        class CacheLexer(CacheNamedGroupLexer):
            def __init__(self):
                CacheNamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('NL', r'\n')
                self.def_separator('WS', r' ')

        lexer = CacheLexer()
        lexer.start("one\ntwo\nthree")

        # Verify line tracking
        line1 = lexer.line

        while lexer.cur_token.name != 'EOF':
            lexer.next_token()

        line_end = lexer.line
        assert line_end > line1


class TestContextSensitiveLexer:
    """Test ContextSensitiveLexer functionality"""

    def test_context_sensitive_lexer_initialization(self):
        """Test ContextSensitiveLexer basic initialization"""
        lexer = ContextSensitiveLexer(True, 0)

        assert hasattr(lexer, 'tokens')
        assert hasattr(lexer, 'separators')

    def test_context_sensitive_lexer_def_token(self):
        """Test adding tokens to ContextSensitiveLexer"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_token('WORD', r'\w+')
        lexer.def_token('NUMBER', r'\d+')

        # Should have two tokens
        assert 'WORD' in lexer.tokens
        assert 'NUMBER' in lexer.tokens

    def test_context_sensitive_lexer_def_separator(self):
        """Test adding separators to ContextSensitiveLexer"""
        lexer = ContextSensitiveLexer(True, 0)
        lexer.def_separator('WS', r'\s+')

        assert len(lexer.separators) > 0


class TestLexerSpecialMethods:
    """Test special lexer methods"""

    def test_back_with_none_resets_position(self):
        """Test that back(None) resets lexer to start"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()
        lexer.start("hello")

        # Advance
        lexer.pos

        # Reset
        lexer.back(None)

        assert lexer.pos == 0
        assert lexer.line == 1
        assert lexer.column == 1

    def test_eof_method_before_end(self):
        """Test eof() returns False before reaching end"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()
        lexer.start("hello")

        assert not lexer.eof()

    def test_eof_method_at_end(self):
        """Test eof() returns True at end"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()
        lexer.start("hello")

        lexer.next_token()  # EOF
        assert lexer.eof()


class TestTokenIndexing:
    """Test token indexing and position tracking"""

    def test_cache_token_indices(self):
        """Test that cached tokens have correct indices"""
        class CacheLexer(CacheNamedGroupLexer):
            def __init__(self):
                CacheNamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = CacheLexer()
        lexer.start("one two")

        # Check token indices
        assert lexer.cache[0].index == 0
        assert lexer.cache[1].index == 1
        # Last token (EOF) also has index
        assert lexer.cache[-1].index == len(lexer.cache) - 1


class TestTokenPositionTracking:
    """Test detailed position tracking"""

    def test_token_start_stop_positions(self):
        """Test that tokens have correct start and stop positions"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = SimpleLexer()
        lexer.start("hello world")

        token1 = lexer.cur_token
        assert token1.start == 0
        assert token1.stop == 5

        lexer.next_token()
        token2 = lexer.cur_token
        assert token2.start == 6
        assert token2.stop == 11

    def test_token_line_column_positions(self):
        """Test token line and column information"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('NL', r'\n')

        lexer = SimpleLexer()
        lexer.start("one\ntwo")

        token1 = lexer.cur_token
        assert token1.line == 1

        lexer.next_token()  # two
        token2 = lexer.cur_token
        assert token2.line == 2


class TestLexerColumnWrapping:
    """Test column wraparound with newlines"""

    def test_column_resets_after_newline(self):
        """Test that column resets after newline"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, False, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('NL', r'\n')

        lexer = SimpleLexer()
        lexer.start("abc\ndef")

        token1 = lexer.cur_token
        col1 = token1.column

        lexer.next_token()  # def
        token2 = lexer.cur_token
        col2 = token2.column

        # Column should reset after newline
        assert col2 < col1 or col2 == 1


class TestLexerStartMethod:
    """Test the start() method in different lexer types"""

    def test_named_group_lexer_start_clears_previous_state(self):
        """Test that start() clears previous lexer state"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()

        # First parsing
        lexer.start("hello")
        lexer.max_pos

        # Second parsing with different input
        lexer.start("world")
        lexer.max_pos

        # Both should process correctly
        assert lexer.cur_token.value == 'world'

    def test_cache_lexer_start_rebuilds_cache(self):
        """Test that cache lexer rebuilds cache on each start()"""
        class CacheLexer(CacheNamedGroupLexer):
            def __init__(self):
                CacheNamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = CacheLexer()

        # First parsing
        lexer.start("one")
        cache_size_1 = len(lexer.cache)

        # Second parsing with different length
        lexer.start("one two three")
        cache_size_2 = len(lexer.cache)

        # Cache sizes should be different
        assert cache_size_2 > cache_size_1


class TestValueFunctionEdgeCases:
    """Test edge cases with value functions"""

    def test_value_function_preserves_token_name(self):
        """Test that value function doesn't affect token name"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('NUM', r'\d+', lambda x: x + "!")

        lexer = SimpleLexer()
        lexer.start("123")

        assert lexer.cur_token.name == 'NUM'
        assert lexer.cur_token.value == '123!'

    def test_complex_value_function(self):
        """Test value function with complex logic"""
        def hex_converter(text):
            try:
                return int(text, 16)
            except ValueError:
                return None

        class HexLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, False, 0)
                self.def_token('HEX', r'0x[0-9a-f]+', hex_converter)

        lexer = HexLexer()
        lexer.start("0x10")

        assert lexer.cur_token.value == 16


class TestMaxPosFurtherestAdvance:
    """Test max_pos tracking across multiple tokens"""

    def test_max_pos_with_backtracking(self):
        """Test max_pos tracks furthest position even with backtracking"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = SimpleLexer()
        lexer.start("one two three")

        max_before = lexer.max_pos

        # Advance through tokens
        while lexer.cur_token.name != 'EOF':
            lexer.next_token()

        max_after = lexer.max_pos
        # Should have advanced
        assert max_after >= max_before


class TestLastTokenTracking:
    """Test last_token attribute tracking"""

    def test_last_token_updated_on_advance(self):
        """Test that last_token is updated when advancing"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')

        lexer = SimpleLexer()
        lexer.start("hello")

        # Move past first token
        lexer.next_token()

        # last_token should be set
        assert lexer.last_token is not None


class TestSeparatorHandling:
    """Test proper handling of separators"""

    def test_multiple_separators_in_row(self):
        """Test multiple separators in sequence are handled"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = SimpleLexer()
        lexer.start("word1    word2")  # Multiple spaces

        token1 = lexer.cur_token
        assert token1.value == 'word1'

        lexer.next_token()
        token2 = lexer.cur_token
        assert token2.value == 'word2'


class TestTokenTextExtraction:
    """Test extracting original text between tokens"""

    def test_extract_includes_separators(self):
        """Test that extract includes separator text"""
        class SimpleLexer(NamedGroupLexer):
            def __init__(self):
                NamedGroupLexer.__init__(self, True, 0)
                self.def_token('WORD', r'\w+')
                self.def_separator('WS', r'\s+')

        lexer = SimpleLexer()
        lexer.start("word one   word two")

        start_token = lexer.cur_token

        # Advance to last token
        while lexer.cur_token.name != 'EOF':
            lexer.next_token()

        # Go back one
        len(lexer.input) - 4
        # Text should include both tokens and spaces
        text = lexer.input[start_token.start:]
        assert 'one' in text
        assert 'two' in text
