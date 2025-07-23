import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';

// A simple debounce function
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const debounce = <T extends (...args: any[]) => void>(func: T, delay: number) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      func(...args);
    }, delay);
  };
};

interface TransliterateInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  value: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  lang: string;
}

const TransliterateInput: React.FC<TransliterateInputProps> = ({ value, onChange, lang, ...props }) => {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const fetchSuggestions = useCallback(async (text: string) => {
    if (!text.trim() || lang !== 'hi') {
      setShowSuggestions(false);
      return;
    }

    try {
      const response = await fetch(`https://inputtools.google.com/request?text=${encodeURIComponent(text)}&itc=hi-t-i0-und&num=5&ie=utf-8&oe=utf-8`);
      const data = await response.json();
      if (data && data[0] === 'SUCCESS' && data[1] && data[1][0] && data[1][0][1]) {
        const newSuggestions = data[1][0][1];
        if (newSuggestions.length > 0) {
          setSuggestions(newSuggestions);
          setShowSuggestions(true);
          setActiveSuggestionIndex(0);
        } else {
          setShowSuggestions(false);
        }
      } else {
        setShowSuggestions(false);
      }
    } catch (error) {
      console.error('Error fetching transliteration suggestions:', error);
      setShowSuggestions(false);
    }
  }, [lang]);

  const debouncedFetch = useMemo(() => debounce(fetchSuggestions, 300), [fetchSuggestions]);

  useEffect(() => {
    const words = value.split(' ');
    const lastWord = words[words.length - 1];
    debouncedFetch(lastWord);
  }, [value, debouncedFetch]);

  const handleSuggestionClick = (suggestion: string) => {
    const words = value.split(' ');
    words[words.length - 1] = suggestion;
    const newValue = words.join(' ') + ' ';

    const syntheticEvent = {
      target: {
        value: newValue,
      },
    } as React.ChangeEvent<HTMLInputElement>;
    
    onChange(syntheticEvent);

    setShowSuggestions(false);
    setSuggestions([]);
  };
  
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (showSuggestions && suggestions.length > 0) {
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        setActiveSuggestionIndex(prevIndex => (prevIndex + 1) % suggestions.length);
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        setActiveSuggestionIndex(prevIndex => (prevIndex - 1 + suggestions.length) % suggestions.length);
      } else if (event.key === 'Enter' || event.key === 'Tab') {
          if (suggestions[activeSuggestionIndex]) {
              event.preventDefault();
              handleSuggestionClick(suggestions[activeSuggestionIndex]);
          }
      } else if (event.key === ' ') {
          if(suggestions[0]){
            event.preventDefault();
            handleSuggestionClick(suggestions[0]);
          }
      } else if (event.key === 'Escape') {
        event.preventDefault();
        setShowSuggestions(false);
      }
    }
    if(props.onKeyDown) {
        props.onKeyDown(event);
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  return (
    <div ref={containerRef} className="w-full relative">
      <input {...props} value={value} onChange={onChange} onKeyDown={handleKeyDown} />
      {showSuggestions && suggestions.length > 0 && lang === 'hi' && (
        <ul className="absolute z-10 w-auto bg-white border border-gray-300 rounded-md shadow-lg bottom-full mb-1" style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {suggestions.map((suggestion, index) => (
            <li
              key={suggestion}
              onClick={() => handleSuggestionClick(suggestion)}
              onMouseOver={() => setActiveSuggestionIndex(index)}
              className={`p-2 cursor-pointer text-gray-800 ${index === activeSuggestionIndex ? 'bg-gray-200' : 'hover:bg-gray-100'}`}
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TransliterateInput; 