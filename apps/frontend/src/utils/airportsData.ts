/**
 * Airport data utility for ICAO code validation and lookup
 * This replaces the vulnerable airport-codes package
 */

export interface Airport {
  icao: string;
  iata?: string;
  name: string;
  city: string;
  country: string;
}

// Major airports ICAO codes database
// This is a curated subset of commonly used airports for METAR reports
export const airportsData: Airport[] = [
  // United States
  { icao: "KATL", iata: "ATL", name: "Hartsfield-Jackson Atlanta International Airport", city: "Atlanta", country: "United States" },
  { icao: "KORD", iata: "ORD", name: "Chicago O'Hare International Airport", city: "Chicago", country: "United States" },
  { icao: "KDFW", iata: "DFW", name: "Dallas/Fort Worth International Airport", city: "Dallas", country: "United States" },
  { icao: "KLAX", iata: "LAX", name: "Los Angeles International Airport", city: "Los Angeles", country: "United States" },
  { icao: "KDEN", iata: "DEN", name: "Denver International Airport", city: "Denver", country: "United States" },
  { icao: "KJFK", iata: "JFK", name: "John F. Kennedy International Airport", city: "New York", country: "United States" },
  { icao: "KSFO", iata: "SFO", name: "San Francisco International Airport", city: "San Francisco", country: "United States" },
  { icao: "KSEA", iata: "SEA", name: "Seattle-Tacoma International Airport", city: "Seattle", country: "United States" },
  { icao: "KLAS", iata: "LAS", name: "Harry Reid International Airport", city: "Las Vegas", country: "United States" },
  { icao: "KMCO", iata: "MCO", name: "Orlando International Airport", city: "Orlando", country: "United States" },
  { icao: "KMIA", iata: "MIA", name: "Miami International Airport", city: "Miami", country: "United States" },
  { icao: "KBOS", iata: "BOS", name: "Boston Logan International Airport", city: "Boston", country: "United States" },
  { icao: "KPHX", iata: "PHX", name: "Phoenix Sky Harbor International Airport", city: "Phoenix", country: "United States" },
  { icao: "KEWR", iata: "EWR", name: "Newark Liberty International Airport", city: "Newark", country: "United States" },
  { icao: "KIAH", iata: "IAH", name: "George Bush Intercontinental Airport", city: "Houston", country: "United States" },
  { icao: "KMSP", iata: "MSP", name: "Minneapolis-St Paul International Airport", city: "Minneapolis", country: "United States" },
  { icao: "KDTW", iata: "DTW", name: "Detroit Metropolitan Wayne County Airport", city: "Detroit", country: "United States" },
  { icao: "KPHL", iata: "PHL", name: "Philadelphia International Airport", city: "Philadelphia", country: "United States" },
  { icao: "KLGA", iata: "LGA", name: "LaGuardia Airport", city: "New York", country: "United States" },
  { icao: "KBWI", iata: "BWI", name: "Baltimore/Washington International Airport", city: "Baltimore", country: "United States" },
  { icao: "KDCA", iata: "DCA", name: "Ronald Reagan Washington National Airport", city: "Washington", country: "United States" },
  { icao: "KIAD", iata: "IAD", name: "Washington Dulles International Airport", city: "Washington", country: "United States" },
  { icao: "KMDW", iata: "MDW", name: "Chicago Midway International Airport", city: "Chicago", country: "United States" },
  { icao: "KPDX", iata: "PDX", name: "Portland International Airport", city: "Portland", country: "United States" },
  { icao: "KSAN", iata: "SAN", name: "San Diego International Airport", city: "San Diego", country: "United States" },
  { icao: "KTPA", iata: "TPA", name: "Tampa International Airport", city: "Tampa", country: "United States" },
  { icao: "KSLC", iata: "SLC", name: "Salt Lake City International Airport", city: "Salt Lake City", country: "United States" },
  { icao: "KSTL", iata: "STL", name: "St. Louis Lambert International Airport", city: "St. Louis", country: "United States" },
  { icao: "KCLT", iata: "CLT", name: "Charlotte Douglas International Airport", city: "Charlotte", country: "United States" },
  { icao: "KAUS", iata: "AUS", name: "Austin-Bergstrom International Airport", city: "Austin", country: "United States" },
  { icao: "KJAX", iata: "JAX", name: "Jacksonville International Airport", city: "Jacksonville", country: "United States" },
  { icao: "KOAK", iata: "OAK", name: "Oakland International Airport", city: "Oakland", country: "United States" },
  { icao: "KSNA", iata: "SNA", name: "John Wayne Airport", city: "Santa Ana", country: "United States" },
  { icao: "KRDU", iata: "RDU", name: "Raleigh-Durham International Airport", city: "Raleigh", country: "United States" },
  { icao: "KMSY", iata: "MSY", name: "Louis Armstrong New Orleans International Airport", city: "New Orleans", country: "United States" },
  { icao: "KCVG", iata: "CVG", name: "Cincinnati/Northern Kentucky International Airport", city: "Cincinnati", country: "United States" },
  { icao: "KSMF", iata: "SMF", name: "Sacramento International Airport", city: "Sacramento", country: "United States" },
  { icao: "KPIT", iata: "PIT", name: "Pittsburgh International Airport", city: "Pittsburgh", country: "United States" },
  { icao: "KCLE", iata: "CLE", name: "Cleveland Hopkins International Airport", city: "Cleveland", country: "United States" },
  { icao: "KBNA", iata: "BNA", name: "Nashville International Airport", city: "Nashville", country: "United States" },
  { icao: "KHOU", iata: "HOU", name: "William P. Hobby Airport", city: "Houston", country: "United States" },
  { icao: "KDAY", iata: "DAY", name: "James M. Cox Dayton International Airport", city: "Dayton", country: "United States" },
  { icao: "KOKC", iata: "OKC", name: "Will Rogers World Airport", city: "Oklahoma City", country: "United States" },
  { icao: "KOMA", iata: "OMA", name: "Eppley Airfield", city: "Omaha", country: "United States" },
  { icao: "KRIC", iata: "RIC", name: "Richmond International Airport", city: "Richmond", country: "United States" },
  { icao: "KMEM", iata: "MEM", name: "Memphis International Airport", city: "Memphis", country: "United States" },
  { icao: "KBUF", iata: "BUF", name: "Buffalo Niagara International Airport", city: "Buffalo", country: "United States" },
  { icao: "KONT", iata: "ONT", name: "Ontario International Airport", city: "Ontario", country: "United States" },
  { icao: "KBUR", iata: "BUR", name: "Bob Hope Airport", city: "Burbank", country: "United States" },
  { icao: "KABI", iata: "ABI", name: "Abilene Regional Airport", city: "Abilene", country: "United States" },
  { icao: "KALB", iata: "ALB", name: "Albany International Airport", city: "Albany", country: "United States" },
  { icao: "KABQ", iata: "ABQ", name: "Albuquerque International Sunport", city: "Albuquerque", country: "United States" },
  { icao: "KANC", iata: "ANC", name: "Ted Stevens Anchorage International Airport", city: "Anchorage", country: "United States" },
  
  // Canada
  { icao: "CYYZ", iata: "YYZ", name: "Toronto Pearson International Airport", city: "Toronto", country: "Canada" },
  { icao: "CYVR", iata: "YVR", name: "Vancouver International Airport", city: "Vancouver", country: "Canada" },
  { icao: "CYUL", iata: "YUL", name: "Montréal-Pierre Elliott Trudeau International Airport", city: "Montreal", country: "Canada" },
  { icao: "CYYC", iata: "YYC", name: "Calgary International Airport", city: "Calgary", country: "Canada" },
  { icao: "CYHZ", iata: "YHZ", name: "Halifax Stanfield International Airport", city: "Halifax", country: "Canada" },
  { icao: "CYEG", iata: "YEG", name: "Edmonton International Airport", city: "Edmonton", country: "Canada" },
  { icao: "CYWG", iata: "YWG", name: "Winnipeg James Armstrong Richardson International Airport", city: "Winnipeg", country: "Canada" },
  { icao: "CYOW", iata: "YOW", name: "Ottawa Macdonald-Cartier International Airport", city: "Ottawa", country: "Canada" },
  
  // United Kingdom
  { icao: "EGLL", iata: "LHR", name: "London Heathrow Airport", city: "London", country: "United Kingdom" },
  { icao: "EGKK", iata: "LGW", name: "London Gatwick Airport", city: "London", country: "United Kingdom" },
  { icao: "EGSS", iata: "STN", name: "London Stansted Airport", city: "London", country: "United Kingdom" },
  { icao: "EGGW", iata: "LTN", name: "London Luton Airport", city: "London", country: "United Kingdom" },
  { icao: "EGCC", iata: "MAN", name: "Manchester Airport", city: "Manchester", country: "United Kingdom" },
  { icao: "EGPH", iata: "EDI", name: "Edinburgh Airport", city: "Edinburgh", country: "United Kingdom" },
  { icao: "EGPF", iata: "GLA", name: "Glasgow Airport", city: "Glasgow", country: "United Kingdom" },
  { icao: "EGGD", iata: "BRS", name: "Bristol Airport", city: "Bristol", country: "United Kingdom" },
  { icao: "EGNX", iata: "EMA", name: "East Midlands Airport", city: "Nottingham", country: "United Kingdom" },
  { icao: "EGBB", iata: "BHX", name: "Birmingham Airport", city: "Birmingham", country: "United Kingdom" },
  
  // Europe
  { icao: "LFPG", iata: "CDG", name: "Charles de Gaulle Airport", city: "Paris", country: "France" },
  { icao: "LFPO", iata: "ORY", name: "Paris Orly Airport", city: "Paris", country: "France" },
  { icao: "EDDF", iata: "FRA", name: "Frankfurt Airport", city: "Frankfurt", country: "Germany" },
  { icao: "EDDM", iata: "MUC", name: "Munich Airport", city: "Munich", country: "Germany" },
  { icao: "EDDB", iata: "BER", name: "Berlin Brandenburg Airport", city: "Berlin", country: "Germany" },
  { icao: "EHAM", iata: "AMS", name: "Amsterdam Airport Schiphol", city: "Amsterdam", country: "Netherlands" },
  { icao: "LEMD", iata: "MAD", name: "Adolfo Suárez Madrid-Barajas Airport", city: "Madrid", country: "Spain" },
  { icao: "LEBL", iata: "BCN", name: "Barcelona-El Prat Airport", city: "Barcelona", country: "Spain" },
  { icao: "LIRF", iata: "FCO", name: "Leonardo da Vinci-Fiumicino Airport", city: "Rome", country: "Italy" },
  { icao: "LIMC", iata: "MXP", name: "Milan Malpensa Airport", city: "Milan", country: "Italy" },
  { icao: "LOWW", iata: "VIE", name: "Vienna International Airport", city: "Vienna", country: "Austria" },
  { icao: "LSZH", iata: "ZRH", name: "Zurich Airport", city: "Zurich", country: "Switzerland" },
  { icao: "EKCH", iata: "CPH", name: "Copenhagen Airport", city: "Copenhagen", country: "Denmark" },
  { icao: "ESSA", iata: "ARN", name: "Stockholm Arlanda Airport", city: "Stockholm", country: "Sweden" },
  { icao: "ENGM", iata: "OSL", name: "Oslo Airport, Gardermoen", city: "Oslo", country: "Norway" },
  { icao: "EFHK", iata: "HEL", name: "Helsinki-Vantaa Airport", city: "Helsinki", country: "Finland" },
  { icao: "EBBR", iata: "BRU", name: "Brussels Airport", city: "Brussels", country: "Belgium" },
  { icao: "LPPT", iata: "LIS", name: "Lisbon Portela Airport", city: "Lisbon", country: "Portugal" },
  { icao: "EIDW", iata: "DUB", name: "Dublin Airport", city: "Dublin", country: "Ireland" },
  { icao: "LKPR", iata: "PRG", name: "Václav Havel Airport Prague", city: "Prague", country: "Czech Republic" },
  { icao: "LHBP", iata: "BUD", name: "Budapest Ferenc Liszt International Airport", city: "Budapest", country: "Hungary" },
  { icao: "EPWA", iata: "WAW", name: "Warsaw Chopin Airport", city: "Warsaw", country: "Poland" },
  { icao: "LGAV", iata: "ATH", name: "Athens International Airport", city: "Athens", country: "Greece" },
  { icao: "LTFM", iata: "IST", name: "Istanbul Airport", city: "Istanbul", country: "Turkey" },
  { icao: "UUEE", iata: "SVO", name: "Sheremetyevo International Airport", city: "Moscow", country: "Russia" },
  { icao: "UUDD", iata: "DME", name: "Domodedovo International Airport", city: "Moscow", country: "Russia" },
  
  // Asia
  { icao: "RJTT", iata: "HND", name: "Tokyo Haneda Airport", city: "Tokyo", country: "Japan" },
  { icao: "RJAA", iata: "NRT", name: "Narita International Airport", city: "Tokyo", country: "Japan" },
  { icao: "RJBB", iata: "KIX", name: "Kansai International Airport", city: "Osaka", country: "Japan" },
  { icao: "RKSI", iata: "ICN", name: "Incheon International Airport", city: "Seoul", country: "South Korea" },
  { icao: "VHHH", iata: "HKG", name: "Hong Kong International Airport", city: "Hong Kong", country: "Hong Kong" },
  { icao: "WSSS", iata: "SIN", name: "Singapore Changi Airport", city: "Singapore", country: "Singapore" },
  { icao: "VTBS", iata: "BKK", name: "Suvarnabhumi Airport", city: "Bangkok", country: "Thailand" },
  { icao: "WMKK", iata: "KUL", name: "Kuala Lumpur International Airport", city: "Kuala Lumpur", country: "Malaysia" },
  { icao: "WIII", iata: "CGK", name: "Soekarno-Hatta International Airport", city: "Jakarta", country: "Indonesia" },
  { icao: "RPLL", iata: "MNL", name: "Ninoy Aquino International Airport", city: "Manila", country: "Philippines" },
  { icao: "ZBAA", iata: "PEK", name: "Beijing Capital International Airport", city: "Beijing", country: "China" },
  { icao: "ZSPD", iata: "PVG", name: "Shanghai Pudong International Airport", city: "Shanghai", country: "China" },
  { icao: "ZGGG", iata: "CAN", name: "Guangzhou Baiyun International Airport", city: "Guangzhou", country: "China" },
  { icao: "ZUUU", iata: "CTU", name: "Chengdu Shuangliu International Airport", city: "Chengdu", country: "China" },
  { icao: "VIDP", iata: "DEL", name: "Indira Gandhi International Airport", city: "New Delhi", country: "India" },
  { icao: "VABB", iata: "BOM", name: "Chhatrapati Shivaji Maharaj International Airport", city: "Mumbai", country: "India" },
  { icao: "VOBL", iata: "BLR", name: "Kempegowda International Airport", city: "Bangalore", country: "India" },
  { icao: "OMDB", iata: "DXB", name: "Dubai International Airport", city: "Dubai", country: "United Arab Emirates" },
  { icao: "OTHH", iata: "DOH", name: "Hamad International Airport", city: "Doha", country: "Qatar" },
  
  // Australia & Oceania
  { icao: "YSSY", iata: "SYD", name: "Sydney Airport", city: "Sydney", country: "Australia" },
  { icao: "YMML", iata: "MEL", name: "Melbourne Airport", city: "Melbourne", country: "Australia" },
  { icao: "YBBN", iata: "BNE", name: "Brisbane Airport", city: "Brisbane", country: "Australia" },
  { icao: "YPPH", iata: "PER", name: "Perth Airport", city: "Perth", country: "Australia" },
  { icao: "NZAA", iata: "AKL", name: "Auckland Airport", city: "Auckland", country: "New Zealand" },
  { icao: "NZCH", iata: "CHC", name: "Christchurch International Airport", city: "Christchurch", country: "New Zealand" },
  
  // South America
  { icao: "SBGR", iata: "GRU", name: "São Paulo/Guarulhos International Airport", city: "São Paulo", country: "Brazil" },
  { icao: "SBGL", iata: "GIG", name: "Rio de Janeiro/Galeão International Airport", city: "Rio de Janeiro", country: "Brazil" },
  { icao: "SCEL", iata: "SCL", name: "Arturo Merino Benítez International Airport", city: "Santiago", country: "Chile" },
  { icao: "SAEZ", iata: "EZE", name: "Ministro Pistarini International Airport", city: "Buenos Aires", country: "Argentina" },
  { icao: "SKBO", iata: "BOG", name: "El Dorado International Airport", city: "Bogotá", country: "Colombia" },
  { icao: "SPIM", iata: "LIM", name: "Jorge Chávez International Airport", city: "Lima", country: "Peru" },
  
  // Africa
  { icao: "FACT", iata: "CPT", name: "Cape Town International Airport", city: "Cape Town", country: "South Africa" },
  { icao: "FAOR", iata: "JNB", name: "O. R. Tambo International Airport", city: "Johannesburg", country: "South Africa" },
  { icao: "HECA", iata: "CAI", name: "Cairo International Airport", city: "Cairo", country: "Egypt" },
  { icao: "GMMN", iata: "CAS", name: "Mohammed V International Airport", city: "Casablanca", country: "Morocco" },
  { icao: "HAAB", iata: "ADD", name: "Addis Ababa Bole International Airport", city: "Addis Ababa", country: "Ethiopia" },
  
  // Mexico & Central America
  { icao: "MMMX", iata: "MEX", name: "Mexico City International Airport", city: "Mexico City", country: "Mexico" },
  { icao: "MMUN", iata: "CUN", name: "Cancún International Airport", city: "Cancún", country: "Mexico" },
  { icao: "MMGL", iata: "GDL", name: "Guadalajara International Airport", city: "Guadalajara", country: "Mexico" },
  { icao: "MMMY", iata: "MTY", name: "Monterrey International Airport", city: "Monterrey", country: "Mexico" },
  { icao: "MROC", iata: "SJO", name: "Juan Santamaría International Airport", city: "San José", country: "Costa Rica" },
  { icao: "MPTO", iata: "PTY", name: "Tocumen International Airport", city: "Panama City", country: "Panama" },
];

/**
 * Create a map for fast ICAO lookups
 */
const airportsByIcao = new Map<string, Airport>();
airportsData.forEach(airport => {
  airportsByIcao.set(airport.icao.toUpperCase(), airport);
});

/**
 * Airport utility functions
 */
export const airports = {
  /**
   * Find an airport by ICAO code
   */
  findWhere(criteria: { icao?: string }): Airport | undefined {
    if (criteria.icao) {
      return airportsByIcao.get(criteria.icao.toUpperCase());
    }
    return undefined;
  },

  /**
   * Get all airports as an array
   */
  toJSON(): Airport[] {
    return airportsData;
  },

  /**
   * Search airports by ICAO prefix
   */
  searchByIcao(prefix: string, limit = 10): Airport[] {
    const upperPrefix = prefix.toUpperCase();
    return airportsData
      .filter(apt => apt.icao.startsWith(upperPrefix))
      .slice(0, limit);
  },

  /**
   * Validate if an ICAO code exists
   */
  isValid(icao: string): boolean {
    return airportsByIcao.has(icao.toUpperCase());
  }
};
