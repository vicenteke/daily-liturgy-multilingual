
if ( null != window.Schott ) {
  window.Schott.loadedData( {
	'2026-12-18' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : 'Wochentag 7 Tage vor Weihnachten',
		NON_PROPRIUM : [ {
				EXPR         : 'constDate(18,12,-1)',
				KEY          : 'advent_17_24_2',
				LEVEL        : 9,
				LEVEL_WOCHE  : 9,
				NAME_DE      : 'Wochentag 7 Tage vor Weihnachten',
				RULE         : 'Am 18.12. des Kalendervorjahres',
				URL_WOCHE_D  : 'advent/Dez_17_24/Dezember',
				url          : 'advent/Dez_17_24/Dezember18.htm'
			} ],
		PROPRIUM     : null,
		STB          : 3
	},
	'2026-12-19' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : 'Samstag der 3. Woche im Advent',
		NON_PROPRIUM : [ {
				KEY          : 'circle_W_3_2027',
				LEVEL        : 9,
				NAME_DE      : 'Samstag der 3. Woche im Advent',
				RULE         : 'Samstag in der 3. Woche gez\xe4hlt beginnend vom 1. Advent',
				url          : 'advent/Dez_17_24/Dezember19.htm'
			} ],
		PROPRIUM     : null,
		STB          : 3
	},
	'2026-12-20' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : '4. Advent',
		NON_PROPRIUM : [ {
				EXPR         : 'sundayAfter(17,12,-1)',
				KEY          : 'advent_4',
				LEVEL        : 2,
				LEVEL_WOCHE  : 9,
				NAME_DE      : '4. Advent',
				RULE         : '1 Wo vor 24.12 / au\xdfer 24.12 = Sonntag: dann f\xe4llt der 4. Advent aus',
				URL_DATE_L   : 'advent/Dez_17_24/Sonntag',
				URL_WOCHE_D  : 'advent/Dez_17_24/Dezember',
				url          : 'advent/Dez_17_24/SonntagB.htm'
			} ],
		PROPRIUM     : null,
		STB          : 4
	},
	'2026-12-21' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : 'Montag der 4. Woche im Advent',
		NON_PROPRIUM : [ {
				KEY          : 'circle_W_4_2027',
				LEVEL        : 9,
				NAME_DE      : 'Montag der 4. Woche im Advent',
				RULE         : 'Montag in der 4. Woche gez\xe4hlt beginnend vom 1. Advent',
				url          : 'advent/Dez_17_24/Dezember21.htm'
			} ],
		PROPRIUM     : null,
		STB          : 4
	},
	'2026-12-22' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : 'Dienstag der 4. Woche im Advent',
		NON_PROPRIUM : [ {
				KEY          : 'circle_W_4_2027',
				LEVEL        : 9,
				NAME_DE      : 'Dienstag der 4. Woche im Advent',
				RULE         : 'Dienstag in der 4. Woche gez\xe4hlt beginnend vom 1. Advent',
				url          : 'advent/Dez_17_24/Dezember22.htm'
			} ],
		PROPRIUM     : null,
		STB          : 4
	},
	'2026-12-23' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : 'Mittwoch der 4. Woche im Advent',
		NON_PROPRIUM : [ {
				KEY          : 'circle_W_4_2027',
				LEVEL        : 9,
				NAME_DE      : 'Mittwoch der 4. Woche im Advent',
				RULE         : 'Mittwoch in der 4. Woche gez\xe4hlt beginnend vom 1. Advent',
				url          : 'advent/Dez_17_24/Dezember23.htm'
			} ],
		PROPRIUM     : [ {
				DESCRIPTION  : 'Priester (+ 1473)',
				EXPR         : 'constDate(23,12,-1)',
				FIX_DATE     : '12-23',
				IS_PROPRIUM  : 1,
				KEY          : '_12_23',
				LEVEL        : 14,
				NAME_DE      : 'Hl. Johannes von Krakau',
				RULE         : 'Am 23.12. des Kalendervorjahres',
				TYPE_D       : 'g',
				TYPE_N       : 'h',
				url          : 'proprium/Dezember23.htm'
			} ],
		STB          : 4
	},
	'2026-12-24' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : 'Weihnachten - Heiliger Abend',
		NON_PROPRIUM : [ {
				EXPR         : 'constDate(24,12,-1)',
				KEY          : 'xmas_0',
				LEVEL        : 2,
				LEVEL_WOCHE  : 9,
				NAME_DE      : 'Weihnachten - Heiliger Abend',
				RULE         : 'Am 24.12. des Kalendervorjahres',
				URL_DATE     : 'weihnachtszeit/weihnachten_register.htm',
				URL_WOCHE_D  : 'advent/Dez_17_24/Dezember',
				url          : 'weihnachtszeit/weihnachten_register.htm'
			} ],
		PROPRIUM     : null,
		STB          : 4
	},
	'2026-12-25' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : 'Weihnachten - Hochfest der Geburt des Herrn',
		NON_PROPRIUM : [ {
				EXPR         : 'constDate(25,12,-1)',
				KEY          : 'xmas_1',
				LEVEL        : 2,
				LEVEL_WOCHE  : 9,
				NAME_DE      : 'Weihnachten - Hochfest der Geburt des Herrn',
				RULE         : 'Am 25.12. des Kalendervorjahres',
				URL_DATE     : 'weihnachtszeit/weihnachten_register.htm',
				URL_WOCHE_D  : 'weihnachtszeit/oktav_',
				url          : 'weihnachtszeit/weihnachten_register.htm'
			} ],
		PROPRIUM     : null,
		STB          : 4
	},
	'2026-12-26' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : 'Hl. Stephanus',
		NON_PROPRIUM : [ {
				EXPR         : 'constDate(26,12,-1)',
				KEY          : 'xmas_2',
				LEVEL        : 9,
				LEVEL_SO     : 7,
				LEVEL_WOCHE  : 9,
				NAME_DE      : '26. Dezember, 2.Tag der Weihnachtsoktav',
				RULE         : 'Am 26.12. des Kalendervorjahres',
				URL_DATE     : 'proprium/Dezember26.htm',
				URL_WOCHE_D  : 'weihnachtszeit/oktav_',
				url          : 'proprium/Dezember26.htm'
			} ],
		PROPRIUM     : [ {
				DESCRIPTION  : 'erster M\xe4rtyrer',
				EXPR         : 'constDate(26,12,-1)',
				FIX_DATE     : '12-26',
				IS_PROPRIUM  : 1,
				KEY          : '_12_26',
				LEVEL        : 7,
				NAME_DE      : 'Hl. Stephanus',
				RULE         : 'Am 26.12. des Kalendervorjahres',
				TYPE_D       : 'F',
				TYPE_N       : 'h',
				url          : 'proprium/Dezember26.htm'
			} ],
		STB          : 4
	},
	'2026-12-27' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : '1. Sonntag nach Weihnachten ~ Fest der Heiligen Familie',
		NON_PROPRIUM : [ {
				EXPR         : 'do{ my $d = sundayAfter(25,12,-1); $d->getMonth == 12 ? $d : constDate(30,12,-1) }',
				KEY          : 'hl_family',
				LEVEL        : 6,
				LEVEL_WOCHE  : 9,
				NAME_DE      : '1. Sonntag nach Weihnachten ~ Fest der Heiligen Familie',
				RULE         : '1. So. nach Weihnachten, oder 30.12. wenn der Sonntag nicht in der Oktav liegt',
				URL_DATE_L   : 'weihnachtszeit/heilige_familie',
				URL_WOCHE_D  : 'weihnachtszeit/oktav_',
				url          : 'weihnachtszeit/heilige_familieB.htm'
			}, {
				EXPR         : 'constDate(27,12,-1)',
				KEY          : 'w_oktav27',
				LEVEL        : 9,
				LEVEL_SO     : 7,
				LEVEL_WOCHE  : 9,
				NAME_DE      : '27. Dezember, 3.Tag der Weihnachtsoktav',
				RULE         : 'Am 27.12. des Kalendervorjahres',
				URL_DATE     : 'proprium/Dezember27.htm',
				URL_WOCHE_D  : 'weihnachtszeit/oktav_',
				url          : 'proprium/Dezember27.htm'
			} ],
		PROPRIUM     : [ {
				DESCRIPTION  : 'Apostel, Evangelist',
				EXPR         : 'constDate(27,12,-1)',
				FIX_DATE     : '12-27',
				IS_PROPRIUM  : 1,
				KEY          : '_12_27',
				LEVEL        : 7,
				NAME_DE      : 'Hl. Johannes',
				RULE         : 'Am 27.12. des Kalendervorjahres',
				TYPE_D       : 'F',
				TYPE_N       : 'h',
				url          : 'proprium/Dezember27.htm'
			} ],
		STB          : 1
	},
	'2026-12-28' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : 'Unschuldige Kinder',
		NON_PROPRIUM : [ {
				EXPR         : 'constDate(28,12,-1)',
				KEY          : 'w_oktav28',
				LEVEL        : 7,
				LEVEL_SO     : 7,
				LEVEL_WOCHE  : 9,
				NAME_DE      : '28. Dezember, 4.Tag der Weihnachtsoktav',
				RULE         : 'Am 28.12. des Kalendervorjahres',
				URL_DATE     : 'proprium/Dezember28.htm',
				URL_WOCHE_D  : 'weihnachtszeit/oktav_',
				url          : 'proprium/Dezember28.htm'
			} ],
		PROPRIUM     : [ {
				EXPR         : 'constDate(28,12,-1)',
				FIX_DATE     : '12-28',
				IS_PROPRIUM  : 1,
				KEY          : '_12_28',
				LEVEL        : 7,
				NAME_DE      : 'Unschuldige Kinder',
				RULE         : 'Am 28.12. des Kalendervorjahres',
				TYPE_D       : 'F',
				TYPE_N       : '',
				url          : 'proprium/Dezember28.htm'
			} ],
		STB          : 1
	},
	'2026-12-29' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : '29. Dezember, 5.Tag der Weihnachtsoktav',
		NON_PROPRIUM : [ {
				EXPR         : 'constDate(29,12,-1)',
				KEY          : 'w_oktav29',
				LEVEL        : 9,
				LEVEL_SO     : 7,
				LEVEL_WOCHE  : 9,
				NAME_DE      : '29. Dezember, 5.Tag der Weihnachtsoktav',
				RULE         : 'Am 29.12. des Kalendervorjahres',
				URL_DATE     : 'weihnachtszeit/oktav_29.htm',
				URL_WOCHE_D  : 'weihnachtszeit/oktav_',
				url          : 'weihnachtszeit/oktav_29.htm'
			} ],
		PROPRIUM     : [ {
				DESCRIPTION  : 'Bischof, M\xe4rtyrer (+ 1170)',
				EXPR         : 'constDate(29,12,-1)',
				FIX_DATE     : '12-29',
				IS_PROPRIUM  : 1,
				KEY          : '_12_29',
				LEVEL        : 14,
				NAME_DE      : 'Hl. Thomas Becket',
				RULE         : 'Am 29.12. des Kalendervorjahres',
				TYPE_D       : 'g',
				TYPE_N       : 'h',
				url          : 'proprium/Dezember29.htm'
			} ],
		STB          : 1
	},
	'2026-12-30' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : '30. Dezember, 6.Tag der Weihnachtsoktav',
		NON_PROPRIUM : [ {
				EXPR         : 'constDate(30,12,-1)',
				KEY          : 'w_oktav30',
				LEVEL        : 9,
				LEVEL_SO     : 7,
				LEVEL_WOCHE  : 9,
				NAME_DE      : '30. Dezember, 6.Tag der Weihnachtsoktav',
				RULE         : 'Am 30.12. des Kalendervorjahres',
				URL_DATE     : 'weihnachtszeit/oktav_30.htm',
				URL_WOCHE_D  : 'weihnachtszeit/oktav_',
				url          : 'weihnachtszeit/oktav_30.htm'
			} ],
		PROPRIUM     : null,
		STB          : 1
	},
	'2026-12-31' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : '31. Dezember, 7.Tag der Weihnachtsoktav',
		NON_PROPRIUM : [ {
				EXPR         : 'constDate(31,12,-1)',
				KEY          : 'silvester',
				LEVEL        : 9,
				LEVEL_SO     : 7,
				LEVEL_WOCHE  : 9,
				NAME_DE      : '31. Dezember, 7.Tag der Weihnachtsoktav',
				RULE         : 'Am 31.12. des Kalendervorjahres',
				URL_DATE     : 'weihnachtszeit/oktav_31.htm',
				URL_WOCHE_D  : 'weihnachtszeit/januar_',
				url          : 'weihnachtszeit/oktav_31.htm'
			} ],
		PROPRIUM     : [ {
				DESCRIPTION  : 'Papst (+ 335)',
				EXPR         : 'constDate(31,12,-1)',
				FIX_DATE     : '12-31',
				IS_PROPRIUM  : 1,
				KEY          : '_12_31',
				LEVEL        : 14,
				NAME_DE      : 'Hl. Silvester I.',
				RULE         : 'Am 31.12. des Kalendervorjahres',
				TYPE_D       : 'g',
				TYPE_N       : 'h',
				url          : 'proprium/Dezember31.htm'
			} ],
		STB          : 1
	},
	'2027-01-01' : {
		LESEJAHR_S   : 2,
		LESEJAHR_W   : 1,
		NAME_DE      : 'Maria',
		NON_PROPRIUM : [ {
				EXPR         : 'constDate(1,1,0)',
				KEY          : 'new_year',
				LEVEL        : 5,
				LEVEL_SO     : 6,
				LEVEL_WOCHE  : 13,
				NAME_DE      : 'Oktavtag von Weihnachten',
				RULE         : 'Am 1.1. des Kalenderjahres',
				URL_DATE     : 'weihnachtszeit/oktavtag.htm',
				URL_WOCHE_D  : 'weihnachtszeit/januar_',
				url          : 'weihnachtszeit/oktavtag.htm'
			} ],
		PROPRIUM     : [ {
				DESCRIPTION  : 'Hochfest der Gottesmutter (Oktavtag von Weihnachten)',
				EXPR         : 'constDate(1,1,0)',
				FIX_DATE     : '01-01',
				IS_PROPRIUM  : 1,
				KEY          : '_01_01_weihnachtszeit/oktavtag.htm',
				LEVEL        : 3,
				NAME_DE      : 'Maria',
				RULE         : 'Am 1.1. des Kalenderjahres',
				TYPE_D       : 'H',
				TYPE_N       : '',
				url          : 'weihnachtszeit/oktavtag.htm'
			} ],
		STB          : 1
	}
} );
}