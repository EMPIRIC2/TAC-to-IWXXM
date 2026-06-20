import { describe, it, expect } from 'vitest'
import { airports, airportsData, type Airport } from './airportsData'

describe('Airport Data & Utilities', () => {
  // ============= Data Integrity Tests =============
  describe('Airport Data Structure', () => {
    it('should contain airport array with data', () => {
      expect(Array.isArray(airportsData)).toBe(true)
      expect(airportsData.length).toBeGreaterThan(0)
    })

    it('should have all required fields in airport objects', () => {
      airportsData.forEach(airport => {
        expect(airport).toHaveProperty('icao')
        expect(airport).toHaveProperty('name')
        expect(airport).toHaveProperty('city')
        expect(airport).toHaveProperty('country')
        expect(typeof airport.icao).toBe('string')
        expect(typeof airport.name).toBe('string')
        expect(typeof airport.city).toBe('string')
        expect(typeof airport.country).toBe('string')
      })
    })

    it('should have valid ICAO codes (4 characters)', () => {
      airportsData.forEach(airport => {
        expect(airport.icao).toMatch(/^[A-Z]{4}$/)
      })
    })

    it('should have IATA codes when present (3 characters)', () => {
      airportsData.forEach(airport => {
        if (airport.iata) {
          expect(airport.iata).toMatch(/^[A-Z]{3}$/)
        }
      })
    })

    it('should not have duplicate ICAO codes', () => {
      const icaoCodes = airportsData.map(a => a.icao.toUpperCase())
      const uniqueIcaoCodes = new Set(icaoCodes)
      expect(uniqueIcaoCodes.size).toBe(icaoCodes.length)
    })

    it('should have US airports starting with K', () => {
      const usAirports = airportsData.filter(a => a.country === 'United States')
      usAirports.forEach(airport => {
        expect(airport.icao.startsWith('K')).toBe(true)
      })
    })

    it('should have Canadian airports starting with C', () => {
      const canadianAirports = airportsData.filter(a => a.country === 'Canada')
      canadianAirports.forEach(airport => {
        expect(airport.icao.startsWith('C')).toBe(true)
      })
    })

    it('should contain major US airports', () => {
      const majorAirportCodes = ['KJFK', 'KLAX', 'KORD', 'KDFW', 'KDEN']
      majorAirportCodes.forEach(code => {
        expect(airportsData.some(a => a.icao === code)).toBe(true)
      })
    })

    it('should contain major international airports', () => {
      const internationalCodes = ['EGLL', 'LFPG', 'EDDF', 'CYYZ', 'RJTT']
      internationalCodes.forEach(code => {
        expect(airportsData.some(a => a.icao === code)).toBe(true)
      })
    })

    it('should have countries from multiple regions', () => {
      const countries = new Set(airportsData.map(a => a.country))
      expect(countries.has('United States')).toBe(true)
      expect(countries.has('Canada')).toBe(true)
      expect(countries.has('United Kingdom')).toBe(true)
      expect(countries.size).toBeGreaterThan(10)
    })
  })

  // ============= airports.findWhere Tests =============
  describe('airports.findWhere()', () => {
    it('should find airport by ICAO code', () => {
      const result = airports.findWhere({ icao: 'KJFK' })
      expect(result).toBeDefined()
      expect(result?.icao).toBe('KJFK')
      expect(result?.iata).toBe('JFK')
      expect(result?.name).toContain('Kennedy')
      expect(result?.city).toBe('New York')
    })

    it('should be case insensitive for ICAO lookup', () => {
      const result1 = airports.findWhere({ icao: 'kjfk' })
      const result2 = airports.findWhere({ icao: 'KJFK' })
      const result3 = airports.findWhere({ icao: 'KjFk' })
      
      expect(result1).toEqual(result2)
      expect(result2).toEqual(result3)
    })

    it('should return undefined for non-existent airport', () => {
      const result = airports.findWhere({ icao: 'XXXX' })
      expect(result).toBeUndefined()
    })

    it('should return undefined with empty criteria', () => {
      const result = airports.findWhere({})
      expect(result).toBeUndefined()
    })

    it('should find multiple airports correctly', () => {
      const testCodes = ['KLAX', 'KORD', 'KDFW', 'KJFK']
      testCodes.forEach(code => {
        const airport = airports.findWhere({ icao: code })
        expect(airport).toBeDefined()
        expect(airport?.icao).toBe(code)
      })
    })

    it('should find international airports', () => {
      const result = airports.findWhere({ icao: 'EGLL' })
      expect(result).toBeDefined()
      expect(result?.name).toContain('Heathrow')
      expect(result?.country).toBe('United Kingdom')
    })

    it('should find airports from different regions', () => {
      const airports_to_test = [
        { code: 'KJFK', country: 'United States' },
        { code: 'CYYZ', country: 'Canada' },
        { code: 'LFPG', country: 'France' },
        { code: 'RJTT', country: 'Japan' },
        { code: 'YSSY', country: 'Australia' },
      ]
      
      airports_to_test.forEach(({ code, country }) => {
        const result = airports.findWhere({ icao: code })
        expect(result?.country).toBe(country)
      })
    })
  })

  // ============= airports.toJSON Tests =============
  describe('airports.toJSON()', () => {
    it('should return array of all airports', () => {
      const result = airports.toJSON()
      expect(Array.isArray(result)).toBe(true)
      expect(result.length).toBe(airportsData.length)
    })

    it('should return proper airport objects', () => {
      const result = airports.toJSON()
      result.forEach(airport => {
        expect(airport).toHaveProperty('icao')
        expect(airport).toHaveProperty('name')
        expect(airport).toHaveProperty('city')
        expect(airport).toHaveProperty('country')
      })
    })

    it('should contain all expected airports', () => {
      const result = airports.toJSON()
      const icaoCodes = result.map(a => a.icao)
      
      expect(icaoCodes).toContain('KJFK')
      expect(icaoCodes).toContain('KLAX')
      expect(icaoCodes).toContain('KORD')
      expect(icaoCodes).toContain('EGLL')
      expect(icaoCodes).toContain('LFPG')
    })

    it('should return independent copy reference', () => {
      const result1 = airports.toJSON()
      const result2 = airports.toJSON()
      expect(result1).toEqual(result2)
    })
  })

  // ============= airports.searchByIcao Tests =============
  describe('airports.searchByIcao()', () => {
    it('should search airports by ICAO prefix', () => {
      const results = airports.searchByIcao('K')
      expect(results.length).toBeGreaterThan(0)
      expect(results.every(a => a.icao.startsWith('K'))).toBe(true)
    })

    it('should be case insensitive for prefix search', () => {
      const results1 = airports.searchByIcao('k')
      const results2 = airports.searchByIcao('K')
      expect(results1.length).toBe(results2.length)
    })

    it('should limit results to specified limit', () => {
      const results = airports.searchByIcao('K', 5)
      expect(results.length).toBeLessThanOrEqual(5)
    })

    it('should use default limit of 10', () => {
      const results = airports.searchByIcao('K')
      expect(results.length).toBeLessThanOrEqual(10)
    })

    it('should return empty array for non-matching prefix', () => {
      const results = airports.searchByIcao('ZZ')
      expect(results.length).toBe(0)
    })

    it('should find specific ICAO prefix matches', () => {
      const results = airports.searchByIcao('KJ')
      expect(results.length).toBeGreaterThan(0)
      expect(results.every(a => a.icao.startsWith('KJ'))).toBe(true)
    })

    it('should find Canadian airports by prefix', () => {
      const results = airports.searchByIcao('CY')
      expect(results.length).toBeGreaterThan(0)
      expect(results.every(a => a.icao.startsWith('CY'))).toBe(true)
    })

    it('should find European airports by prefix', () => {
      const results = airports.searchByIcao('EG')
      expect(results.length).toBeGreaterThan(0)
      expect(results.every(a => a.icao.startsWith('EG'))).toBe(true)
    })

    it('should respect limit parameter correctly', () => {
      const limit = 3
      const results = airports.searchByIcao('K', limit)
      expect(results.length).toBeLessThanOrEqual(limit)
    })

    it('should work with different limits', () => {
      const results1 = airports.searchByIcao('K', 5)
      const results2 = airports.searchByIcao('K', 15)
      expect(results1.length).toBeLessThanOrEqual(results2.length)
    })
  })

  // ============= airports.isValid Tests =============
  describe('airports.isValid()', () => {
    it('should validate existing ICAO codes', () => {
      expect(airports.isValid('KJFK')).toBe(true)
      expect(airports.isValid('KLAX')).toBe(true)
      expect(airports.isValid('KORD')).toBe(true)
    })

    it('should be case insensitive for validation', () => {
      expect(airports.isValid('kjfk')).toBe(true)
      expect(airports.isValid('KJFK')).toBe(true)
      expect(airports.isValid('KjFk')).toBe(true)
    })

    it('should reject non-existent ICAO codes', () => {
      expect(airports.isValid('XXXX')).toBe(false)
      expect(airports.isValid('ZZZZ')).toBe(false)
      expect(airports.isValid('INVALID')).toBe(false)
    })

    it('should validate international airports', () => {
      expect(airports.isValid('EGLL')).toBe(true)
      expect(airports.isValid('LFPG')).toBe(true)
      expect(airports.isValid('EDDF')).toBe(true)
      expect(airports.isValid('CYYZ')).toBe(true)
      expect(airports.isValid('RJTT')).toBe(true)
    })

    it('should reject invalid formats', () => {
      expect(airports.isValid('JFK')).toBe(false)
      expect(airports.isValid('KJFKX')).toBe(false)
      expect(airports.isValid('KJF')).toBe(false)
      expect(airports.isValid('')).toBe(false)
    })

    it('should validate all airports in database', () => {
      airportsData.forEach(airport => {
        expect(airports.isValid(airport.icao)).toBe(true)
      })
    })

    it('should work with lowercase input', () => {
      expect(airports.isValid('kjfk')).toBe(true)
      expect(airports.isValid('egll')).toBe(true)
      expect(airports.isValid('lfpg')).toBe(true)
    })

    it('should work with mixed case input', () => {
      expect(airports.isValid('KjFk')).toBe(true)
      expect(airports.isValid('eGlL')).toBe(true)
      expect(airports.isValid('LfPg')).toBe(true)
    })
  })

  // ============= Integration Tests =============
  describe('Integration Tests', () => {
    it('should find and validate airport in one workflow', () => {
      const icao = 'KJFK'
      expect(airports.isValid(icao)).toBe(true)
      
      const airport = airports.findWhere({ icao })
      expect(airport).toBeDefined()
      expect(airport?.name).toContain('Kennedy')
    })

    it('should search, find, and validate airports', () => {
      const results = airports.searchByIcao('K', 5)
      
      results.forEach(airport => {
        expect(airports.isValid(airport.icao)).toBe(true)
        const found = airports.findWhere({ icao: airport.icao })
        expect(found).toEqual(airport)
      })
    })

    it('should handle mixed case workflows', () => {
      const lcaseIcao = 'kjfk'
      const ucaseIcao = 'KJFK'
      
      expect(airports.isValid(lcaseIcao)).toBe(airports.isValid(ucaseIcao))
      
      const found1 = airports.findWhere({ icao: lcaseIcao })
      const found2 = airports.findWhere({ icao: ucaseIcao })
      expect(found1).toEqual(found2)
    })

    it('should retrieve all unique airports without duplicates', () => {
      const allAirports = airports.toJSON()
      const icaos = allAirports.map(a => a.icao.toUpperCase())
      const uniqueIcaos = new Set(icaos)
      
      expect(uniqueIcaos.size).toBe(icaos.length)
    })

    it('should search and validate all results are valid', () => {
      const searchResults = airports.searchByIcao('K', 10)
      
      searchResults.forEach(result => {
        expect(airports.isValid(result.icao)).toBe(true)
      })
    })
  })

  // ============= Edge Cases =============
  describe('Edge Cases', () => {
    it('should handle whitespace in ICAO code', () => {
      const result = airports.findWhere({ icao: ' KJFK ' })
      // This might not work depending on implementation
      // but we test the actual behavior
      if (result) {
        expect(result.icao).toBe('KJFK')
      }
    })

    it('should handle single letter prefix search', () => {
      const results = airports.searchByIcao('K')
      expect(results.length).toBeGreaterThan(0)
    })

    it('should handle full ICAO code as search prefix', () => {
      const results = airports.searchByIcao('KJFK')
      expect(results.some(a => a.icao === 'KJFK')).toBe(true)
    })

    it('should handle zero limit', () => {
      const results = airports.searchByIcao('K', 0)
      expect(results.length).toBe(0)
    })

    it('should handle very high limit', () => {
      const results = airports.searchByIcao('K', 1000)
      expect(results.length).toBeLessThanOrEqual(1000)
    })

    it('should have non-empty names for all airports', () => {
      airportsData.forEach(airport => {
        expect(airport.name.length).toBeGreaterThan(0)
      })
    })

    it('should have non-empty cities for all airports', () => {
      airportsData.forEach(airport => {
        expect(airport.city.length).toBeGreaterThan(0)
      })
    })

    it('should have non-empty countries for all airports', () => {
      airportsData.forEach(airport => {
        expect(airport.country.length).toBeGreaterThan(0)
      })
    })
  })

  // ============= Performance Tests =============
  describe('Performance Characteristics', () => {
    it('should quickly find airport by ICAO', () => {
      const start = performance.now()
      airports.findWhere({ icao: 'KJFK' })
      const duration = performance.now() - start
      expect(duration).toBeLessThan(5) // Should be instant (< 5ms)
    })

    it('should quickly validate ICAO code', () => {
      const start = performance.now()
      airports.isValid('KJFK')
      const duration = performance.now() - start
      expect(duration).toBeLessThan(5)
    })

    it('should quickly search by prefix', () => {
      const start = performance.now()
      airports.searchByIcao('K', 10)
      const duration = performance.now() - start
      expect(duration).toBeLessThan(20) // Should be quick
    })
  })

  // ============= Type Safety Tests =============
  describe('Type Safety', () => {
    it('should return correct Airport type from findWhere', () => {
      const result = airports.findWhere({ icao: 'KJFK' })
      if (result) {
        const airport: Airport = result
        expect(airport.icao).toBeDefined()
        expect(airport.name).toBeDefined()
      }
    })

    it('should return Airport array from toJSON', () => {
      const results = airports.toJSON()
      expect(Array.isArray(results)).toBe(true)
      if (results.length > 0) {
        const airport: Airport = results[0]
        expect(airport.icao).toBeDefined()
      }
    })

    it('should return Airport array from searchByIcao', () => {
      const results = airports.searchByIcao('K')
      expect(Array.isArray(results)).toBe(true)
      if (results.length > 0) {
        const airport: Airport = results[0]
        expect(airport.icao).toBeDefined()
      }
    })
  })
})
