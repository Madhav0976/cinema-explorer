"""Mock TMDB API fixtures for deterministic testing."""

MOCK_TELUGU_MOVIE = {
    "id": 579974,
    "title": "RRR",
    "original_title": "రౌద్రం రణం రుధిరం",
    "overview": "A fictional history of two legendary revolutionaries' journey away from home.",
    "release_date": "2022-03-24",
    "poster_path": "/wE0noFU94b5U3ZfSpVj0wG37l0v.jpg",
    "backdrop_path": "/707thQ440Bup13o9p5B0hD1C3n1.jpg",
    "original_language": "te",
    "vote_average": 8.0,
    "vote_count": 1400,
    "popularity": 45.2,
    "genres": [
        {"id": 28, "name": "Action"},
        {"id": 18, "name": "Drama"},
    ],
    "spoken_languages": [
        {"iso_639_1": "te", "name": "తెలుగు", "english_name": "Telugu"},
        {"iso_639_1": "hi", "name": "हिन्दी", "english_name": "Hindi"},
    ],
    "production_countries": [
        {"iso_3166_1": "IN", "name": "India"},
    ],
    "credits": {
        "cast": [
            {"id": 11111, "name": "N. T. Rama Rao Jr.", "character": "Komaram Bheem", "profile_path": "/ntr.jpg"},
            {"id": 11112, "name": "Ram Charan", "character": "Alluri Sitarama Raju", "profile_path": "/rc.jpg"},
        ],
        "crew": [
            {"id": 11113, "name": "S. S. Rajamouli", "job": "Director", "department": "Directing", "profile_path": "/ssr.jpg"},
            {"id": 11114, "name": "M. M. Keeravani", "job": "Original Music Composer", "department": "Sound", "profile_path": "/mmk.jpg"},
        ],
    },
    "alternative_titles": {
        "titles": [
            {"iso_3166_1": "US", "title": "RRR: Rise Roar Revolt"},
            {"iso_3166_1": "IN", "title": "Roudram Ranam Rudhiram"},
        ]
    },
    "external_ids": {
        "imdb_id": "tt8178634",
        "wikidata_id": "Q60303473",
    },
    "watch/providers": {
        "results": {
            "IN": {
                "link": "https://www.themoviedb.org/movie/579974/watch?locale=IN",
                "flatrate": [
                    {"provider_id": 8, "provider_name": "Netflix", "logo_path": "/netflix.jpg"},
                    {"provider_id": 119, "provider_name": "Amazon Prime Video", "logo_path": "/prime.jpg"},
                ],
                "rent": [
                    {"provider_id": 3, "provider_name": "Google Play Movies", "logo_path": "/gplay.jpg"},
                ],
            }
        }
    },
}

MOCK_JAPANESE_ANIME_MOVIE = {
    "id": 129,
    "title": "Spirited Away",
    "original_title": "千と千尋の神隠し",
    "overview": "A 10-year-old girl wanders into a world ruled by gods, witches, and spirits.",
    "release_date": "2001-07-20",
    "poster_path": "/393t3h.jpg",
    "backdrop_path": "/Ab8mk.jpg",
    "original_language": "ja",
    "vote_average": 8.5,
    "vote_count": 16000,
    "popularity": 95.0,
    "genres": [
        {"id": 16, "name": "Animation"},
        {"id": 10751, "name": "Family"},
        {"id": 14, "name": "Fantasy"},
    ],
    "spoken_languages": [
        {"iso_639_1": "ja", "name": "日本語", "english_name": "Japanese"},
    ],
    "production_countries": [
        {"iso_3166_1": "JP", "name": "Japan"},
    ],
    "production_companies": [
        {"id": 10342, "name": "Studio Ghibli", "origin_country": "JP"},
    ],
    "keywords": {
        "keywords": [
            {"id": 210024, "name": "anime"},
            {"id": 1500, "name": "spirit"},
        ]
    },
    "credits": {
        "cast": [
            {"id": 22221, "name": "Rumi Hiiragi", "character": "Chihiro Ogino (voice)", "profile_path": "/rumi.jpg"},
        ],
        "crew": [
            {"id": 608, "name": "Hayao Miyazaki", "job": "Director", "department": "Directing", "profile_path": "/miyazaki.jpg"},
        ],
    },
    "alternative_titles": {
        "titles": [
            {"iso_3166_1": "US", "title": "Spirited Away"},
        ]
    },
    "external_ids": {
        "imdb_id": "tt0245429",
        "wikidata_id": "Q155653",
    },
    "watch/providers": {
        "results": {
            "IN": {
                "link": "https://www.themoviedb.org/movie/129/watch?locale=IN",
                "flatrate": [
                    {"provider_id": 8, "provider_name": "Netflix", "logo_path": "/netflix.jpg"},
                ],
            }
        }
    },
}

MOCK_JAPANESE_LIVE_ACTION_MOVIE = {
    "id": 346,
    "title": "Seven Samurai",
    "original_title": "七人の侍",
    "overview": "A poor village under attack by bandits recruits seven unemployed samurai to help them defend themselves.",
    "release_date": "1954-04-26",
    "poster_path": "/samurai.jpg",
    "backdrop_path": "/samurai_bg.jpg",
    "original_language": "ja",
    "vote_average": 8.5,
    "vote_count": 3500,
    "popularity": 32.1,
    "genres": [
        {"id": 28, "name": "Action"},
        {"id": 18, "name": "Drama"},
    ],
    "production_countries": [
        {"iso_3166_1": "JP", "name": "Japan"},
    ],
    "credits": {
        "cast": [{"id": 3331, "name": "Toshiro Mifune", "character": "Kikuchiyo", "profile_path": None}],
        "crew": [{"id": 5026, "name": "Akira Kurosawa", "job": "Director", "department": "Directing", "profile_path": None}],
    },
}

MOCK_WESTERN_ANIMATION_MOVIE = {
    "id": 862,
    "title": "Toy Story",
    "original_title": "Toy Story",
    "overview": "Led by Woody, Andy's toys live happily in his room until Andy's birthday brings Buzz Lightyear.",
    "release_date": "1995-10-30",
    "original_language": "en",
    "genres": [
        {"id": 16, "name": "Animation"},
        {"id": 35, "name": "Comedy"},
    ],
    "production_countries": [
        {"iso_3166_1": "US", "name": "United States of America"},
    ],
    "credits": {"cast": [], "crew": []},
}

MOCK_TV_SERIES = {
    "id": 1396,
    "name": "Breaking Bad",
    "original_name": "Breaking Bad",
    "overview": "A chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine.",
    "first_air_date": "2008-01-20",
    "poster_path": "/bb.jpg",
    "backdrop_path": "/bb_bg.jpg",
    "original_language": "en",
    "vote_average": 8.9,
    "vote_count": 13000,
    "popularity": 120.5,
    "genres": [
        {"id": 18, "name": "Drama"},
        {"id": 80, "name": "Crime"},
    ],
    "spoken_languages": [
        {"iso_639_1": "en", "name": "English", "english_name": "English"},
        {"iso_639_1": "es", "name": "Español", "english_name": "Spanish"},
    ],
    "production_countries": [
        {"iso_3166_1": "US", "name": "United States of America"},
    ],
    "origin_country": ["US"],
    "seasons": [
        {
            "id": 3572,
            "season_number": 1,
            "name": "Season 1",
            "air_date": "2008-01-20",
            "episode_count": 7,
            "poster_path": "/s1.jpg",
        },
        {
            "id": 3573,
            "season_number": 2,
            "name": "Season 2",
            "air_date": "2009-03-08",
            "episode_count": 13,
            "poster_path": "/s2.jpg",
        },
    ],
    "credits": {
        "cast": [
            {"id": 17419, "name": "Bryan Cranston", "character": "Walter White", "profile_path": "/bc.jpg"},
        ],
        "crew": [
            {"id": 66633, "name": "Vince Gilligan", "job": "Executive Producer", "department": "Production", "profile_path": "/vg.jpg"},
        ],
    },
    "alternative_titles": {
        "results": [
            {"iso_3166_1": "US", "title": "Breaking Bad: The Series"},
        ]
    },
    "external_ids": {
        "imdb_id": "tt0903747",
        "wikidata_id": "Q1079",
    },
    "watch/providers": {
        "results": {
            "IN": {
                "link": "https://www.themoviedb.org/tv/1396/watch?locale=IN",
                "flatrate": [
                    {"provider_id": 8, "provider_name": "Netflix", "logo_path": "/netflix.jpg"},
                ],
            }
        }
    },
}

MOCK_ANIME_TV_SERIES = {
    "id": 1429,
    "name": "Attack on Titan",
    "original_name": "進撃の巨人",
    "overview": "Several hundred years ago, humans were nearly exterminated by Titans.",
    "first_air_date": "2013-04-07",
    "poster_path": "/aot.jpg",
    "backdrop_path": "/aot_bg.jpg",
    "original_language": "ja",
    "vote_average": 8.7,
    "vote_count": 6000,
    "popularity": 110.0,
    "genres": [
        {"id": 16, "name": "Animation"},
        {"id": 10759, "name": "Action & Adventure"},
        {"id": 10765, "name": "Sci-Fi & Fantasy"},
    ],
    "origin_country": ["JP"],
    "production_countries": [
        {"iso_3166_1": "JP", "name": "Japan"},
    ],
    "keywords": {
        "results": [
            {"id": 210024, "name": "anime"},
            {"id": 222243, "name": "based on manga"},
        ]
    },
    "seasons": [
        {
            "id": 52994,
            "season_number": 1,
            "name": "Season 1",
            "air_date": "2013-04-07",
            "episode_count": 25,
            "poster_path": "/aot_s1.jpg",
        }
    ],
    "credits": {"cast": [], "crew": []},
}

