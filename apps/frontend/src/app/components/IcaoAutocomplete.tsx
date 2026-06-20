import { useState, useEffect, useRef } from 'react';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { airports } from '../../utils/airportsData';
import { CheckCircle, AlertCircle } from 'lucide-react';

interface IcaoAutocompleteProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  maxLength?: number;
  helperText?: string;
  className?: string;
  id?: string;
}

interface AirportSuggestion {
  icao?: string;
  name?: string;
}

export function IcaoAutocomplete({
  label,
  value,
  onChange,
  placeholder = '',
  maxLength = 4,
  helperText,
  className = '',
  id = 'icao-input',
}: IcaoAutocompleteProps) {
  const [suggestions, setSuggestions] = useState<AirportSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const validateIcao = (code: string): boolean => {
    if (!code || code.length !== 4) return false;
    return airports.isValid(code);
  };

  const handleInputChange = (inputValue: string) => {
    const upperValue = inputValue.toUpperCase();
    onChange(upperValue);

    if (upperValue.length === 0) {
      setSuggestions([]);
      setShowSuggestions(false);
      setIsValid(null);
      return;
    }

    if (upperValue.length === 4) {
      const valid = validateIcao(upperValue);
      setIsValid(valid);
    } else {
      setIsValid(null);
    }

    if (upperValue.length >= 2) {
      try {
        const filtered = airports.searchByIcao(upperValue, 10);
        setSuggestions(filtered);
        setShowSuggestions(filtered.length > 0);
      } catch (error) {
        console.error('Error fetching airports:', error);
        setSuggestions([]);
        setShowSuggestions(false);
      }
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (airport: AirportSuggestion) => {
    const icaoCode = airport.icao || '';
    onChange(icaoCode);
    setIsValid(true);
    setSuggestions([]);
    setShowSuggestions(false);
  };

  return (
    <div className={`relative ${className}`} ref={wrapperRef}>
      <Label htmlFor={id} className="dark:text-white">
        {label}
      </Label>
      <div className="relative">
        <Input
          id={id}
          value={value}
          onChange={(e) => handleInputChange(e.target.value)}
          placeholder={placeholder}
          maxLength={maxLength}
          className={`dark:bg-gray-700 dark:text-white dark:border-gray-600 pr-8 ${
            isValid === true
              ? 'border-green-500 dark:border-green-500'
              : isValid === false
              ? 'border-red-500 dark:border-red-500'
              : ''
          }`}
          autoComplete="off"
        />
        {isValid !== null && (
          <div className="absolute right-2 top-1/2 -translate-y-1/2">
            {isValid ? (
              <CheckCircle className="w-5 h-5 text-green-500" aria-label="Valid ICAO code" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-500" aria-label="Invalid ICAO code" />
            )}
          </div>
        )}
      </div>
      {helperText && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{helperText}</p>
      )}

      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg max-h-60 overflow-auto">
          {suggestions.map((airport, index) => (
            <button
              key={index}
              type="button"
              onClick={() => handleSuggestionClick(airport)}
              className="w-full px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 flex flex-col border-b border-gray-200 dark:border-gray-700 last:border-0"
            >
              <span className="font-semibold text-gray-900 dark:text-white">
                {airport.icao || 'N/A'}
              </span>
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {airport.name || 'Unknown Airport'}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {airport.city || ''}{airport.city && airport.country ? ', ' : ''}{airport.country || ''}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
