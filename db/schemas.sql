--
-- PostgreSQL database dump
--

-- Dumped from database version 15.2 (Debian 15.2-1.pgdg110+1)
-- Dumped by pg_dump version 16.0 (Ubuntu 16.0-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: common; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA common;


--
-- Name: SCHEMA common; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA common IS 'common schema';


--
-- Name: energy; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA energy;


--
-- Name: governance; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA governance;


--
-- Name: SCHEMA governance; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA governance IS 'governance schema';


--
-- Name: infrastructure; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA infrastructure;


--
-- Name: SCHEMA infrastructure; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA infrastructure IS 'infrastructure schema';


--
-- Name: people; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA people;


--
-- Name: SCHEMA people; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA people IS 'people schema';


--
-- Name: property; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA property;


--
-- Name: SCHEMA property; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA property IS 'property schema';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: i_grid_regular(public.geometry, double precision, double precision); Type: FUNCTION; Schema: common; Owner: -
--

CREATE FUNCTION common.i_grid_regular(geom public.geometry, x_side double precision, y_side double precision, OUT public.geometry) RETURNS SETOF public.geometry
    LANGUAGE plpgsql IMMUTABLE STRICT
    AS $_$ DECLARE
x_max DECIMAL;
y_max DECIMAL;
x_min DECIMAL;
y_min DECIMAL;
srid INTEGER := 4326;
input_srid INTEGER;
x_series DECIMAL;
y_series DECIMAL;
geom_cell geometry := ST_GeomFromText(FORMAT('POLYGON((0 0, 0 %s, %s %s, %s 0,0 0))',
											$3, $2, $3, $2), srid);
BEGIN
	CASE ST_SRID (geom) WHEN 0 THEN
		geom := ST_SetSRID (geom, srid);
		RAISE NOTICE'SRID Not Found.';
	ELSE
		RAISE NOTICE'SRID Found.';
	END CASE;
	input_srid := ST_srid ( geom );
	geom := ST_Transform ( geom, srid );
	x_max := ST_XMax ( geom );
	y_max := ST_YMax ( geom );
	x_min := ST_XMin ( geom );
	y_min := ST_YMin ( geom );
	x_series := CEIL ( @( x_max - x_min ) / x_side );
	y_series := CEIL ( @( y_max - y_min ) / y_side );

	RETURN QUERY With foo AS (
		SELECT
		ST_Translate( geom_cell, j * $2 + x_min, i * $3 + y_min ) AS cell
		FROM
			generate_series ( 0, x_series ) AS j,
			generate_series ( 0, y_series ) AS i
		) SELECT ST_CollectionExtract(ST_Collect(ST_Transform ( ST_Intersection(cell, geom), input_srid)), 3)
		FROM foo where ST_intersects (cell, geom);
END;
$_$;


--
-- Name: makegrid(public.geometry, integer); Type: FUNCTION; Schema: common; Owner: -
--

CREATE FUNCTION common.makegrid(public.geometry, integer) RETURNS public.geometry
    LANGUAGE sql
    AS $_$SELECT ST_Collect(ST_POINT(x, y)) FROM 
generate_series(floor(ST_XMIN($1))::int, ceiling(ST_XMAX($1)-ST_XMIN($1))::int, $2) AS x,
generate_series(floor(ST_YMIN($1))::int, ceiling(ST_YMAX($1)-ST_YMIN($1))::int, $2) AS y 
WHERE st_intersects($1, ST_POINT(x, y))$_$;


--
-- Name: sales_tables_detail(integer); Type: FUNCTION; Schema: property; Owner: -
--

CREATE FUNCTION property.sales_tables_detail(year_in integer) RETURNS TABLE(date date, price integer, buyer character varying, seller character varying, sale_type smallint, land_use smallint)
    LANGUAGE plpgsql
    AS $$
BEGIN
   RETURN QUERY
	SELECT s.date ,
			s.price ,
			s.buyer ,
			s.seller ,
			s.sale_type ,
			s.land_use 
	FROM property.sales s
	WHERE s.year = year_in
	ORDER BY s.date;
END
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cpi_ts; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.cpi_ts (
    date date,
    value real,
    dor_series character varying(20),
    dor_series_type character varying(20)
);


--
-- Name: election_dates; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.election_dates (
    date date NOT NULL,
    value character varying(20) NOT NULL
);


--
-- Name: graphics_parameters; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.graphics_parameters (
    parameters jsonb
);


--
-- Name: int_value_pairs; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.int_value_pairs (
    key integer NOT NULL,
    item character varying(30) NOT NULL,
    value character varying(255)
);


--
-- Name: loc_pid; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.loc_pid (
    loc_id character(16) NOT NULL,
    year smallint,
    pid character(17) NOT NULL
);


--
-- Name: loc_pid_address; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.loc_pid_address (
    loc_id character(16) NOT NULL,
    pid character(17) NOT NULL,
    addresses smallint,
    address_id integer[]
);


--
-- Name: loc_polygons; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.loc_polygons (
    loc_id character(16) NOT NULL,
    year smallint NOT NULL,
    geometry public.geometry(MultiPolygon,4326),
    lat real,
    lon real
);


--
-- Name: naics; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.naics (
    key integer NOT NULL,
    value character varying(255)
);


--
-- Name: parameters; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.parameters (
    parameter_type smallint NOT NULL,
    dict jsonb
);


--
-- Name: school_id_location; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.school_id_location (
    school_id integer NOT NULL,
    year smallint NOT NULL,
    location character varying(25),
    dor smallint
);


--
-- Name: structures; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.structures (
    dor smallint,
    pid character(17),
    struct_id character(13),
    date date,
    area_sq_ft real,
    area real,
    length real,
    geometry public.geometry(Polygon,4326)
);


--
-- Name: town_boundaries; Type: TABLE; Schema: common; Owner: -
--

CREATE TABLE common.town_boundaries (
    town character varying(30),
    town_id smallint NOT NULL,
    pop1980 integer,
    pop1990 integer,
    pop2000 integer,
    popch90_00 integer,
    type character(2),
    fourcolor character(1),
    fips_stco smallint,
    sum_acres real,
    sum_square real,
    pop2010 integer,
    popch00_10 integer,
    popch80_90 real,
    shape_area real,
    shape_len real,
    geometry public.geometry(Geometry,4326),
    lat real,
    lon real
);


--
-- Name: eia_generator; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.eia_generator (
    utility_id integer NOT NULL,
    plant_code integer NOT NULL,
    generator_id character varying(5) NOT NULL,
    technology character varying(43),
    prime_mover character(2),
    unit_code character varying(4),
    ownership character(1),
    duct_burners character(1),
    steam_recovery character(1),
    node character varying(48),
    location character varying(48),
    "MW" real,
    power_factor real,
    summer_capacity real,
    winter_capacity real,
    minimum_load real,
    rate_deltas boolean,
    rate_month smallint,
    rate_year smallint,
    status character(2),
    grid_sync character(1),
    operating_month smallint,
    operating_year smallint,
    retirement_month smallint,
    retirement_year smallint,
    combo_heat_power boolean,
    sector_name character varying(20),
    sector smallint,
    top_or_bottom character(1),
    energy_source1 character varying(3),
    energy_source2 character varying(3),
    energy_source3 character varying(3),
    energy_source4 character varying(3),
    energy_source5 character varying(3),
    energy_source6 character varying(3),
    startup_source1 character varying(3),
    startup_source2 character varying(3),
    startup_source3 character varying(3),
    startup_source4 character varying(3),
    gassification boolean,
    carbon_capture boolean,
    turbines smallint,
    restart_time character varying(4),
    fluidized_tech boolean,
    pulverized_tech boolean,
    stoker_tech boolean,
    combustion_tech boolean,
    subcritical_tech boolean,
    supercritical_tech boolean,
    ultracritical_tech boolean,
    planned_summer_uprate_capacity real,
    planned_winter_uprate_capacity real,
    planned_uprate_month smallint,
    planned_uprate_year smallint,
    planned_summer_derate_capacity real,
    planned_winter_derate_capacity real,
    planned_derate_month smallint,
    planned_derate_year smallint,
    planned_prime_mover character(2),
    planned_energy_source1 character varying(3),
    planned_capacity real,
    planned_repower_month smallint,
    planned_repower_year smallint,
    other_modifications boolean,
    other_mod_month smallint,
    other_mod_year smallint,
    multiple_fuels boolean,
    cofire boolean,
    oil_natgas_switch boolean
);


--
-- Name: eia_generator_ownership; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.eia_generator_ownership (
    utility_id integer NOT NULL,
    plant_code integer NOT NULL,
    generator_id character varying(5) NOT NULL,
    owner_id integer NOT NULL,
    share real
);


--
-- Name: eia_multifuel; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.eia_multifuel (
    utility_id integer NOT NULL,
    plant_code integer NOT NULL,
    generator_id character varying(5) NOT NULL,
    source1 character varying(3),
    source2 character varying(3),
    multiple boolean,
    cofire boolean,
    cofire1 character varying(3),
    cofire2 character varying(3),
    cofire3 character varying(3),
    cofire4 character varying(3),
    cofire5 character varying(3),
    cofire6 character varying(3),
    oil_natgas_switch boolean,
    operating_switch boolean,
    summer_capacity_natgas real,
    winter_capacity_natgas real,
    summer_capacity_oil real,
    winter_capacity_oil real,
    switching_time_natgas2oil character varying(4),
    switching_time_oil2natgas character varying(4),
    switch_limiting_factors boolean,
    storage_limits boolean,
    air_limits boolean,
    other_limits boolean
);


--
-- Name: eia_owner; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.eia_owner (
    owner_id integer NOT NULL,
    name character varying(75),
    street character varying(80),
    city character varying(20),
    state character(2),
    zip character(5)
);


--
-- Name: eia_plant; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.eia_plant (
    utility_id integer NOT NULL,
    plant_code integer NOT NULL,
    plant_name character varying(56),
    street character varying(30),
    city character varying(30),
    state character(2),
    zip character(5),
    county character varying(25),
    lat real,
    lon real,
    region character varying(4),
    authority_code character varying(4),
    authority character varying(66),
    water_source character varying(30),
    naics character varying(6),
    regulatory_status character(2),
    sector smallint,
    sector_name character varying(18),
    cogeneration boolean,
    docket character varying(60),
    small_pp boolean,
    small_docket character varying(60),
    wholesaler boolean,
    wholesaler_docket character varying(60),
    ash boolean,
    ash_lined character(1),
    ash_status character(2),
    distributor character varying(41),
    distributor_id integer,
    distributor_state character(2),
    grid_voltage real,
    grid_voltage_2 real,
    grid_voltage_3 real,
    storage boolean,
    natgas_ldc_name character varying(36),
    natgas_pipeline1 character varying(47),
    natgas_pipeline2 character varying(47),
    natgas_pipeline3 character varying(47),
    pipeline_notes character varying(255),
    natgas_storage character(1),
    lng_storage character(1)
);


--
-- Name: eia_solar; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.eia_solar (
    utility_id integer NOT NULL,
    plant_code integer NOT NULL,
    generator_id character varying(5) NOT NULL,
    mirrors boolean,
    single_axis boolean,
    dual_axis boolean,
    fixed_tilt boolean,
    east_west_tilt boolean,
    parabolic boolean,
    fresnel boolean,
    tower boolean,
    dish boolean,
    other_tech boolean,
    azimuth real,
    tilt real,
    "MW_dc" real,
    crystaline boolean,
    "thin_film_CdTe" boolean,
    "thin_film_ASi" boolean,
    "thin_film_CIGS" boolean,
    thin_film_other boolean,
    other_materials boolean,
    net_metering character(1),
    net_metering_capacity real,
    net_metering_virtual character(1),
    net_metering_virtual_capacity real
);


--
-- Name: eia_storage; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.eia_storage (
    utility_id integer NOT NULL,
    plant_code integer NOT NULL,
    generator_id character varying(5) NOT NULL,
    "MWh" real,
    max_charge_rate real,
    minimum_discharge_rate real,
    storage_tech1 character(3),
    storage_tech2 character(3),
    storage_tech3 character(3),
    storage_tech4 character(3),
    power_rating real,
    enclosure character(2),
    arb boolean,
    frequency_regulation boolean,
    load_following boolean,
    spinning boolean,
    colocated boolean,
    distribution_deferral boolean,
    peak_shaving boolean,
    load_mgt boolean,
    voltage_support boolean,
    backup boolean,
    excess_solar_wind boolean
);


--
-- Name: eia_utility; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.eia_utility (
    utility_id integer NOT NULL,
    name character varying(61),
    street character varying(30),
    city character varying(30),
    state character(2),
    zip character(5),
    owner boolean,
    operator boolean,
    manager boolean,
    other boolean,
    entity character varying(3)
);


--
-- Name: eia_wind; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.eia_wind (
    utility_id integer NOT NULL,
    plant_code integer NOT NULL,
    generator_id character varying(5) NOT NULL,
    number_turbines smallint,
    manufacturer character varying(20),
    model character varying(15),
    design_speed real,
    quality smallint,
    height real
);


--
-- Name: electric_utility; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.electric_utility (
    pid character(17) NOT NULL,
    start date NOT NULL,
    date date NOT NULL,
    days smallint NOT NULL,
    kwh integer NOT NULL,
    generation real NOT NULL,
    delivery real NOT NULL,
    customer_charge real NOT NULL
);


--
-- Name: gas_utility; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.gas_utility (
    pid character(17) NOT NULL,
    start date NOT NULL,
    date date NOT NULL,
    days smallint NOT NULL,
    therms integer NOT NULL,
    therm_factor real NOT NULL,
    cost_per_therm real NOT NULL,
    min_charge real NOT NULL,
    tier1_delivery real NOT NULL,
    tier1_del_adj real NOT NULL
);


--
-- Name: iso_genfuelmix; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.iso_genfuelmix (
    datetime timestamp without time zone NOT NULL,
    "MW" smallint NOT NULL,
    iso_fuel_cat smallint NOT NULL,
    iso_fuel smallint NOT NULL,
    marginal boolean NOT NULL
);


--
-- Name: iso_lmp; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.iso_lmp (
    location_id smallint NOT NULL,
    datetime timestamp without time zone NOT NULL,
    total real NOT NULL,
    energy real NOT NULL,
    congestion real NOT NULL,
    loss real NOT NULL
);


--
-- Name: iso_system_loads; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.iso_system_loads (
    datetime timestamp without time zone NOT NULL,
    "MW" smallint NOT NULL,
    native real NOT NULL,
    demand real NOT NULL,
    btm_pv real NOT NULL,
    native_btm_pv real NOT NULL
);


--
-- Name: ohms; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.ohms (
    pid character(17) NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    kwh real,
    fridge real,
    dryer real,
    oven real,
    dishwasher real,
    ac real
);


--
-- Name: solar; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.solar (
    dor smallint,
    pid character varying(17),
    date date,
    watt integer,
    cost integer,
    attributes jsonb,
    financials jsonb,
    dates jsonb,
    entity jsonb,
    amps jsonb,
    watts jsonb,
    joules jsonb,
    xref jsonb,
    solar_index integer NOT NULL
);


--
-- Name: solar_bnl; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.solar_bnl (
    dor smallint,
    date date,
    bnl_data_provider_1 smallint,
    bnl_data_provider_2 smallint,
    "system_ID_1" character varying(18) NOT NULL,
    "system_size_DC" real,
    total_installed_price real,
    rebate_or_grant real,
    bnl_customer_segment smallint,
    expansion_system smallint,
    multiple_phase_system smallint,
    tracking smallint,
    ground_mounted smallint,
    bnl_utility_service_territory smallint,
    third_party_owned smallint,
    bnl_installer_name smallint,
    self_installed smallint,
    azimuth_1 smallint,
    azimuth_2 smallint,
    azimuth_3 smallint,
    tilt_1 smallint,
    tilt_2 smallint,
    tilt_3 smallint,
    bnl_module_manufacturer_1 smallint,
    bnl_module_model_1 smallint,
    module_quantity_1 smallint,
    bnl_module_manufacturer_2 smallint,
    bnl_module_model_2 smallint,
    module_quantity_2 smallint,
    bnl_module_manufacturer_3 smallint,
    bnl_module_model_3 smallint,
    module_quantity_3 smallint,
    additional_modules smallint,
    bnl_technology_module_1 smallint,
    bnl_technology_module_2 smallint,
    bnl_technology_module_3 smallint,
    "BIPV_module_1" smallint,
    "BIPV_module_2" smallint,
    "BIPV_module_3" smallint,
    bifacial_module_1 smallint,
    bifacial_module_2 smallint,
    bifacial_module_3 smallint,
    nameplate_capacity_module_1 smallint,
    nameplate_capacity_module_2 smallint,
    nameplate_capacity_module_3 smallint,
    efficiency_module_1 real,
    efficiency_module_2 real,
    efficiency_module_3 real,
    bnl_inverter_manufacturer_1 smallint,
    bnl_inverter_model_1 smallint,
    inverter_quantity_1 smallint,
    bnl_inverter_manufacturer_2 smallint,
    bnl_inverter_model_2 smallint,
    inverter_quantity_2 smallint,
    bnl_inverter_manufacturer_3 smallint,
    bnl_inverter_model_3 smallint,
    inverter_quantity_3 smallint,
    additional_inverters smallint,
    micro_inverter_1 smallint,
    micro_inverter_2 smallint,
    micro_inverter_3 smallint,
    built_in_meter_inverter_1 smallint,
    built_in_meter_inverter_2 smallint,
    built_in_meter_inverter_3 smallint,
    output_capacity_inverter_1 smallint,
    output_capacity_inverter_2 smallint,
    output_capacity_inverter_3 smallint,
    "DC_optimizer" smallint,
    inverter_loading_ratio real,
    "dateOfBatteryInstall" date,
    bnl_battery_manufacturer smallint,
    bnl_battery_model smallint,
    "battery_rated_capacity_kW" smallint,
    "battery_rated_capacity_kWh" smallint
);


--
-- Name: solar_production; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.solar_production (
    pid character(17) NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    kwh real NOT NULL
);


--
-- Name: solar_pts; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.solar_pts (
    dor smallint,
    year smallint,
    date date,
    watt integer,
    cost integer,
    "grant" integer,
    "est_annual_kWh" integer,
    pts_program smallint,
    pts_type smallint,
    pts_installer smallint,
    pts_module_mfgr smallint,
    pts_inverter_mfgr smallint,
    pts_meter_mfgr smallint,
    pts_utility smallint,
    pts_owner smallint,
    pts_srec smallint
);


--
-- Name: solar_rps; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.solar_rps (
    dor smallint,
    rps_id character varying(11),
    date date,
    watt integer,
    cost integer,
    rps_status smallint,
    rps_capacity_block smallint,
    expiration_date date,
    operation_date date,
    rps_distributor smallint,
    applicant character varying(65),
    rps_installer smallint,
    owner character varying(75),
    rps_ownership_type smallint,
    rps_type smallint,
    rps_size smallint,
    watt_ac integer,
    rps_location smallint,
    rps_location_tranche smallint,
    rps_off_taker smallint,
    rps_off_taker_tranche smallint,
    rps_tracking smallint,
    rps_tracking_tranche smallint,
    rps_pollinator smallint,
    rps_pollinator_tranche smallint,
    rps_storage smallint,
    rps_storage_tranche smallint,
    "storage_kVa" real,
    storage_duration real,
    rps_low_income smallint,
    rps_land_use smallint,
    rps_interconnection smallint,
    rps_meter_type smallint,
    rps_standalone smallint,
    nepool_id character varying(20),
    rps_aggregation smallint,
    name character varying(90),
    sq_date date,
    rps_utility smallint,
    rps_sector smallint,
    rps_subsector smallint,
    rps_srec_factor smallint,
    qualification_date date,
    rps_distributer smallint
);


--
-- Name: solar_rps_raw; Type: TABLE; Schema: energy; Owner: -
--

CREATE TABLE energy.solar_rps_raw (
    project text,
    status text,
    capacity_block text,
    expiration_date text,
    operation_date timestamp without time zone,
    effective_date timestamp without time zone,
    distributor text,
    applicant text,
    installer text,
    owner text,
    ownership_type text,
    type text,
    city text,
    zip double precision,
    size text,
    "kW_ac" double precision,
    "kW" double precision,
    location text,
    location_tranche text,
    off_taker text,
    off_taker_tranche text,
    tracking text,
    tracking_tranche text,
    pollinator text,
    pollinator_tranche text,
    storage text,
    storage_tranche text,
    "storage_kVa" double precision,
    storage_duration double precision,
    low_income text,
    land_use text,
    interconnection text,
    meter_type text,
    standalone text,
    cost double precision,
    "perWatt" double precision,
    rps_id text,
    nepool_id text,
    aggregation text,
    name text,
    sq_date timestamp without time zone,
    utility text,
    sector text,
    subsector text,
    srec_factor double precision,
    qualification_date timestamp without time zone,
    distributer text
);


--
-- Name: solar_solar_index_seq; Type: SEQUENCE; Schema: energy; Owner: -
--

CREATE SEQUENCE energy.solar_solar_index_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: solar_solar_index_seq; Type: SEQUENCE OWNED BY; Schema: energy; Owner: -
--

ALTER SEQUENCE energy.solar_solar_index_seq OWNED BY energy.solar.solar_index;


--
-- Name: checkbook; Type: TABLE; Schema: governance; Owner: -
--

CREATE TABLE governance.checkbook (
    dor smallint,
    year smallint,
    date date,
    check_number integer,
    amount real,
    checkbook_vendor smallint,
    checkbook_description smallint,
    checkbook_fund_type smallint,
    checkbook_department_category smallint,
    checkbook_department smallint
);


--
-- Name: dor_databank; Type: TABLE; Schema: governance; Owner: -
--

CREATE TABLE governance.dor_databank (
    dor smallint NOT NULL,
    year smallint NOT NULL,
    dor_databank_series smallint NOT NULL,
    value bigint,
    zscore real
);


--
-- Name: meetings; Type: TABLE; Schema: governance; Owner: -
--

CREATE TABLE governance.meetings (
    dor smallint NOT NULL,
    authority smallint NOT NULL,
    date date NOT NULL,
    meeting_id smallint,
    video character varying(50) NOT NULL,
    transcript text,
    markdown text,
    qa jsonb
);


--
-- Name: meetings_2bDeleted; Type: TABLE; Schema: governance; Owner: -
--

CREATE TABLE governance."meetings_2bDeleted" (
    dor smallint NOT NULL,
    authority smallint NOT NULL,
    date date NOT NULL,
    markdown text
);


--
-- Name: meetings_directory; Type: TABLE; Schema: governance; Owner: -
--

CREATE TABLE governance.meetings_directory (
    dor smallint NOT NULL,
    authority smallint NOT NULL,
    date date NOT NULL,
    meeting_id smallint,
    video character varying(50) NOT NULL
);


--
-- Name: prop25_votes; Type: TABLE; Schema: governance; Owner: -
--

CREATE TABLE governance.prop25_votes (
    dor smallint,
    year smallint,
    date date,
    "Win / Loss" character varying(4),
    "Yes Votes" integer,
    "No Votes" integer,
    vote_type character varying(22),
    "Amount" bigint,
    description character varying(255),
    "Department" character varying(25)
);


--
-- Name: tmm; Type: TABLE; Schema: governance; Owner: -
--

CREATE TABLE governance.tmm (
    precinct smallint,
    name character varying(255),
    address character varying(255),
    term smallint,
    phone character varying(20),
    email character varying(255),
    year smallint,
    people_id character varying(12),
    sex smallint,
    pid character varying(17)
);


--
-- Name: grid; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.grid (
    circuit_id character varying(10) NOT NULL,
    amps smallint,
    substation character varying(25),
    "substation_rating_MVA" smallint,
    substation_type character varying(12),
    bulk_substation character varying(20),
    bulk_substation_voltage smallint,
    "bulk_substation_rating_MVA" smallint,
    "timestamp" integer,
    sections smallint,
    section_id character(15)[],
    "capacity_MW" real[],
    section_voltage real[]
);


--
-- Name: grid_segments; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.grid_segments (
    lats real,
    lons real,
    section_id character(15),
    circuit_id character varying(10)
);


--
-- Name: ppp; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.ppp (
    "BorrowerName" character varying(60),
    "LoanNumber" bigint[],
    "DateApproved" date[],
    "BorrowerAddress" character varying(45),
    "InitialApprovalAmount" integer,
    "CurrentApprovalAmount" integer,
    "UndisbursedAmount" integer,
    "FranchiseName" character varying(45),
    "BusinessAgeDescription" character varying(35),
    "JobsReported" smallint,
    "NAICSCode" integer,
    "Race" character(35),
    "Ethnicity" character varying(30),
    "UTILITIES_PROCEED" integer,
    "PAYROLL_PROCEED" integer,
    "MORTGAGE_INTEREST_PROCEED" integer,
    "RENT_PROCEED" integer,
    "REFINANCE_EIDL_PROCEED" integer,
    "HEALTH_CARE_PROCEED" integer,
    "DEBT_INTEREST_PROCEED" integer,
    "BusinessType" character varying(35),
    "Gender" character varying(15),
    "Veteran" character varying(15),
    "NonProfit" character(1),
    "ForgivenessAmount" integer,
    "ForgivenessDate" date[],
    address character varying(45),
    pid character varying(20)
);


--
-- Name: road_segments; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.road_segments (
    lats real,
    lons real,
    seg_id character(4),
    class smallint
);


--
-- Name: roads; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.roads (
    "streetName" character varying(25),
    from_street character varying(25),
    to_street character varying(25),
    class smallint,
    segments smallint,
    seg_id smallint[],
    median_type character(1),
    median_width smallint,
    right_sidewalk smallint,
    left_sidewalk smallint,
    speed_limit smallint,
    safe_route character varying(25),
    oneway character varying(3),
    length real,
    segment_lengths real[],
    miles real
);


--
-- Name: schools_enrollment; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.schools_enrollment (
    school_id integer NOT NULL,
    year smallint NOT NULL,
    grade character varying(5) NOT NULL,
    value integer
);


--
-- Name: schools_mcas; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.schools_mcas (
    school_id integer NOT NULL,
    year smallint NOT NULL,
    mcas_subject smallint NOT NULL,
    mcas_grade smallint NOT NULL,
    mcas smallint NOT NULL,
    value integer
);


--
-- Name: schools_nss; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.schools_nss (
    school_id integer NOT NULL,
    year smallint NOT NULL,
    nss smallint NOT NULL,
    value integer
);


--
-- Name: schools_ppx; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.schools_ppx (
    school_id integer NOT NULL,
    year smallint NOT NULL,
    ppx smallint NOT NULL,
    value integer
);


--
-- Name: schools_teacher_age; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.schools_teacher_age (
    school_id integer NOT NULL,
    year smallint NOT NULL,
    teacher_age smallint NOT NULL,
    value integer
);


--
-- Name: schools_teacher_program_area; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.schools_teacher_program_area (
    school_id integer NOT NULL,
    year smallint NOT NULL,
    teacher_program_area smallint NOT NULL,
    value integer
);


--
-- Name: schools_teacher_race; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.schools_teacher_race (
    school_id integer NOT NULL,
    year smallint NOT NULL,
    teacher_race smallint NOT NULL,
    value integer
);


--
-- Name: schools_teacher_salaries; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.schools_teacher_salaries (
    school_id integer NOT NULL,
    year smallint NOT NULL,
    teacher_salaries smallint NOT NULL,
    value integer
);


--
-- Name: schools_types; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.schools_types (
    dor smallint NOT NULL,
    year smallint NOT NULL,
    schools_type smallint NOT NULL,
    value integer
);


--
-- Name: water_accounts; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.water_accounts (
    account integer NOT NULL,
    date date NOT NULL,
    pid character varying(17),
    owner character varying(40),
    address character varying(40),
    region character varying(2),
    user_type character(1),
    amount double precision
);


--
-- Name: water_bills; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.water_bills (
    account integer NOT NULL,
    date date NOT NULL,
    usage smallint,
    amount double precision,
    usage_ttm smallint,
    amount_ttm double precision,
    "usage_chg_YoY" double precision,
    "amount_chg_YoY" double precision
);


--
-- Name: activity_type_histogram; Type: TABLE; Schema: people; Owner: -
--

CREATE TABLE people.activity_type_histogram (
    date date,
    age smallint,
    count smallint,
    activity_type smallint
);


--
-- Name: addresses; Type: TABLE; Schema: people; Owner: -
--

CREATE TABLE people.addresses (
    address_id smallint NOT NULL,
    "streetName" character varying(20),
    "streetNum" character varying(5),
    unit character varying(10),
    "streetSuffix" character varying(5),
    pid character varying(17)
);


--
-- Name: attributes; Type: TABLE; Schema: people; Owner: -
--

CREATE TABLE people.attributes (
    people_id character(12) NOT NULL,
    name character varying(50)[],
    date_name date[],
    address_id smallint[],
    date_address_id date[],
    party smallint[],
    date_party date[],
    precinct smallint[],
    date_precinct date[],
    date_dob date,
    dob date,
    sex smallint
);


--
-- Name: elections; Type: TABLE; Schema: people; Owner: -
--

CREATE TABLE people.elections (
    people_id character(12) NOT NULL,
    date date[]
);


--
-- Name: party_histogram; Type: TABLE; Schema: people; Owner: -
--

CREATE TABLE people.party_histogram (
    date date,
    age smallint,
    count smallint,
    party smallint
);


--
-- Name: precinct_histogram; Type: TABLE; Schema: people; Owner: -
--

CREATE TABLE people.precinct_histogram (
    date date,
    age smallint,
    count smallint,
    precinct smallint
);


--
-- Name: registered; Type: TABLE; Schema: people; Owner: -
--

CREATE TABLE people.registered (
    people_id character(12) NOT NULL,
    date date[]
);


--
-- Name: residents; Type: TABLE; Schema: people; Owner: -
--

CREATE TABLE people.residents (
    people_id character(12) NOT NULL,
    date date[]
);


--
-- Name: sex_histogram; Type: TABLE; Schema: people; Owner: -
--

CREATE TABLE people.sex_histogram (
    date date,
    age smallint,
    count smallint,
    sex smallint
);


--
-- Name: assessments; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.assessments (
    streetnum character varying(10),
    streetname character varying(25),
    unit character varying(5),
    building integer,
    land integer,
    other integer,
    total integer,
    area integer,
    last_sale_date date,
    last_sale_price integer,
    land_use smallint,
    zip smallint,
    owner character varying(41),
    owner_city smallint,
    owner_state smallint,
    book character varying(6),
    page character varying(9),
    zoning smallint,
    year_built smallint,
    building_area integer,
    units smallint,
    living_area integer,
    style smallint,
    stories smallint,
    rooms smallint,
    year smallint NOT NULL,
    loc_id2 character varying(16) NOT NULL,
    pid character varying(17) NOT NULL,
    land_chg_1y real,
    land_chg_3y real,
    land_chg_5y real,
    land_chg_10y real,
    total_chg_1y real,
    total_chg_3y real,
    total_chg_5y real,
    total_chg_10y real
);


--
-- Name: deeds_details; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.deeds_details (
    streetnum character varying(10),
    streetname character varying(255),
    unit character varying(255),
    date date,
    "timestamp" real,
    docno integer,
    deed_type smallint,
    book integer,
    page smallint,
    pages smallint,
    consideration integer,
    deeds_status smallint,
    name character varying(255)[],
    grant_type smallint[],
    refs_bookpage character varying(255)[],
    refs_deed_type character varying(255)[],
    refs_deed_year smallint[],
    pid character varying(17),
    registered boolean
);


--
-- Name: deeds_details_raw; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.deeds_details_raw (
    "Street #" character varying(255),
    "Street Name" character varying(255),
    "Description" character varying(255),
    "Doc. #" integer,
    "Rec. Date" date,
    "Rec Time" character varying(255),
    "Type Desc." character varying(255),
    "# of Pgs." smallint,
    "Book/Page" character varying(255),
    "Consideration" integer,
    "Doc. Status" character varying(255),
    name character varying(255)[],
    grant_type smallint[],
    refs_book_page character varying(15)[],
    refs_deed_type character varying(255)[],
    refs_year smallint[]
);


--
-- Name: deeds_details_raw_2bDeleted; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property."deeds_details_raw_2bDeleted" (
    "Street #" character varying(255),
    "Street Name" character varying(255),
    "Description" character varying(255),
    "Doc. #" integer,
    "Rec. Date" date,
    "Rec Time" character varying(255),
    "Type Desc." character varying(255),
    "# of Pgs." smallint,
    "Book/Page" character varying(255),
    "Consideration" integer,
    "Doc. Status" character varying(255),
    name character varying(255)[],
    grant_type smallint[],
    refs_book_page character varying(15)[],
    refs_deed_type character varying(255)[],
    refs_year smallint[]
);


--
-- Name: deeds_parcel_xref; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.deeds_parcel_xref (
    registered boolean,
    date date NOT NULL,
    docno integer NOT NULL,
    bookpage character varying(9),
    "Sale Price" integer,
    parcel character varying(20)[]
);


--
-- Name: deeds_summary; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.deeds_summary (
    date date,
    book integer,
    page smallint,
    deed_type smallint,
    town smallint,
    docno integer
);


--
-- Name: heatpumps; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.heatpumps (
    received date NOT NULL,
    installed date NOT NULL,
    total real NOT NULL,
    occupants smallint,
    footage smallint,
    fuel character varying(50),
    rebate real,
    ac character varying(50),
    heating_costs integer,
    outdoor_units smallint,
    indoor_units smallint,
    capacity integer,
    installer character varying(255),
    backup character varying(255),
    address character varying(255),
    manufacturer character varying(255),
    "streetNum" smallint,
    "streetName" character varying(255),
    "streetSuffix" character varying(20),
    unit character varying(5),
    pid character(17)
);


--
-- Name: mbta_districts; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.mbta_districts (
    pid character(17) NOT NULL,
    land_use smallint NOT NULL
);


--
-- Name: patriot; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.patriot (
    year smallint NOT NULL,
    account integer NOT NULL,
    pid character(17) NOT NULL,
    address character varying(30),
    cards smallint,
    zoning smallint,
    "lotSize" real,
    sketch character varying(12),
    image character varying(16),
    owner jsonb,
    assessments jsonb,
    inspections jsonb,
    yard jsonb,
    permits jsonb,
    previous jsonb,
    sales jsonb,
    condo jsonb,
    condo2 jsonb,
    rooms jsonb,
    alt_finishes jsonb,
    "subAreas" jsonb,
    interior jsonb,
    exterior jsonb
);


--
-- Name: patriot_int_value_pairs; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.patriot_int_value_pairs (
    key smallint NOT NULL,
    description character varying(255),
    item character varying(255) NOT NULL,
    tab character varying(255)
);


--
-- Name: patriot_summary; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.patriot_summary (
    parcel character varying(17) NOT NULL,
    location character varying(30),
    assessed integer,
    luc character(3),
    nhood character varying(4),
    "lotSize" integer,
    "finArea" integer,
    fy smallint NOT NULL
);


--
-- Name: permits; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.permits (
    year smallint NOT NULL,
    date date NOT NULL,
    permit integer NOT NULL,
    permit_type smallint NOT NULL,
    permit_class smallint,
    description text,
    owner character varying(255),
    contractor character varying(255),
    permit_value integer,
    permit_fee integer,
    "streetName" character varying(50),
    "streetNum" character varying(20),
    address character varying(255),
    pid character varying(17)
);


--
-- Name: sales; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.sales (
    "streetName" character varying(23),
    "streetNum" character varying(4),
    unit character varying(5),
    land_use smallint,
    date date,
    price integer,
    buyer character varying(36),
    seller character varying(44),
    sale_type smallint,
    year smallint NOT NULL,
    loc_id character varying(16),
    pid character varying(19)
);


--
-- Name: tax_rates; Type: TABLE; Schema: property; Owner: -
--

CREATE TABLE property.tax_rates (
    year smallint,
    rate real
);


--
-- Name: solar solar_index; Type: DEFAULT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.solar ALTER COLUMN solar_index SET DEFAULT nextval('energy.solar_solar_index_seq'::regclass);


--
-- Name: election_dates election_dates_pkey; Type: CONSTRAINT; Schema: common; Owner: -
--

ALTER TABLE ONLY common.election_dates
    ADD CONSTRAINT election_dates_pkey PRIMARY KEY (date);


--
-- Name: int_value_pairs int_value_pairs_pkey; Type: CONSTRAINT; Schema: common; Owner: -
--

ALTER TABLE ONLY common.int_value_pairs
    ADD CONSTRAINT int_value_pairs_pkey PRIMARY KEY (key, item);


--
-- Name: loc_pid_address loc_pid_address_pkey; Type: CONSTRAINT; Schema: common; Owner: -
--

ALTER TABLE ONLY common.loc_pid_address
    ADD CONSTRAINT loc_pid_address_pkey PRIMARY KEY (loc_id, pid);


--
-- Name: loc_pid loc_pid_pkey; Type: CONSTRAINT; Schema: common; Owner: -
--

ALTER TABLE ONLY common.loc_pid
    ADD CONSTRAINT loc_pid_pkey PRIMARY KEY (loc_id, pid);


--
-- Name: loc_polygons loc_polygons_pkey; Type: CONSTRAINT; Schema: common; Owner: -
--

ALTER TABLE ONLY common.loc_polygons
    ADD CONSTRAINT loc_polygons_pkey PRIMARY KEY (loc_id, year);


--
-- Name: naics naics_pkey; Type: CONSTRAINT; Schema: common; Owner: -
--

ALTER TABLE ONLY common.naics
    ADD CONSTRAINT naics_pkey PRIMARY KEY (key);


--
-- Name: parameters parameters_pkey; Type: CONSTRAINT; Schema: common; Owner: -
--

ALTER TABLE ONLY common.parameters
    ADD CONSTRAINT parameters_pkey PRIMARY KEY (parameter_type);


--
-- Name: school_id_location school_id_location_pkey; Type: CONSTRAINT; Schema: common; Owner: -
--

ALTER TABLE ONLY common.school_id_location
    ADD CONSTRAINT school_id_location_pkey PRIMARY KEY (school_id, year);


--
-- Name: town_boundaries town_boundaries_pkey; Type: CONSTRAINT; Schema: common; Owner: -
--

ALTER TABLE ONLY common.town_boundaries
    ADD CONSTRAINT town_boundaries_pkey PRIMARY KEY (town_id);


--
-- Name: eia_generator_ownership eia_generator_ownership_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.eia_generator_ownership
    ADD CONSTRAINT eia_generator_ownership_pkey PRIMARY KEY (utility_id, plant_code, generator_id, owner_id);


--
-- Name: eia_generator eia_generator_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.eia_generator
    ADD CONSTRAINT eia_generator_pkey PRIMARY KEY (plant_code, generator_id);


--
-- Name: eia_multifuel eia_multifuel_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.eia_multifuel
    ADD CONSTRAINT eia_multifuel_pkey PRIMARY KEY (utility_id, plant_code, generator_id);


--
-- Name: eia_owner eia_owner_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.eia_owner
    ADD CONSTRAINT eia_owner_pkey PRIMARY KEY (owner_id);


--
-- Name: eia_plant eia_plant_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.eia_plant
    ADD CONSTRAINT eia_plant_pkey PRIMARY KEY (plant_code);


--
-- Name: eia_solar eia_solar_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.eia_solar
    ADD CONSTRAINT eia_solar_pkey PRIMARY KEY (utility_id, plant_code, generator_id);


--
-- Name: eia_storage eia_storage_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.eia_storage
    ADD CONSTRAINT eia_storage_pkey PRIMARY KEY (utility_id, plant_code, generator_id);


--
-- Name: eia_utility eia_utility_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.eia_utility
    ADD CONSTRAINT eia_utility_pkey PRIMARY KEY (utility_id);


--
-- Name: eia_wind eia_wind_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.eia_wind
    ADD CONSTRAINT eia_wind_pkey PRIMARY KEY (utility_id, plant_code, generator_id);


--
-- Name: electric_utility electric_utility_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.electric_utility
    ADD CONSTRAINT electric_utility_pkey PRIMARY KEY (pid, date);


--
-- Name: gas_utility gas_utility_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.gas_utility
    ADD CONSTRAINT gas_utility_pkey PRIMARY KEY (pid, date);


--
-- Name: iso_genfuelmix iso_genfuelmix_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.iso_genfuelmix
    ADD CONSTRAINT iso_genfuelmix_pkey PRIMARY KEY (datetime, iso_fuel);


--
-- Name: iso_lmp iso_lmp_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.iso_lmp
    ADD CONSTRAINT iso_lmp_pkey PRIMARY KEY (location_id, datetime);


--
-- Name: iso_system_loads iso_system_loads_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.iso_system_loads
    ADD CONSTRAINT iso_system_loads_pkey PRIMARY KEY (datetime);


--
-- Name: ohms ohms_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.ohms
    ADD CONSTRAINT ohms_pkey PRIMARY KEY (pid, "timestamp");


--
-- Name: solar_bnl solar_bnl_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.solar_bnl
    ADD CONSTRAINT solar_bnl_pkey PRIMARY KEY ("system_ID_1");


--
-- Name: solar_production solar_production_pkey; Type: CONSTRAINT; Schema: energy; Owner: -
--

ALTER TABLE ONLY energy.solar_production
    ADD CONSTRAINT solar_production_pkey PRIMARY KEY (pid, "timestamp");


--
-- Name: dor_databank dor_databank_pkey; Type: CONSTRAINT; Schema: governance; Owner: -
--

ALTER TABLE ONLY governance.dor_databank
    ADD CONSTRAINT dor_databank_pkey PRIMARY KEY (dor, year, dor_databank_series);


--
-- Name: meetings_directory meetings_directory_pkey; Type: CONSTRAINT; Schema: governance; Owner: -
--

ALTER TABLE ONLY governance.meetings_directory
    ADD CONSTRAINT meetings_directory_pkey PRIMARY KEY (dor, authority, date);


--
-- Name: meetings meetings_pkey; Type: CONSTRAINT; Schema: governance; Owner: -
--

ALTER TABLE ONLY governance.meetings
    ADD CONSTRAINT meetings_pkey PRIMARY KEY (dor, authority, date);


--
-- Name: meetings_2bDeleted meetings_pkey_2bDeleted; Type: CONSTRAINT; Schema: governance; Owner: -
--

ALTER TABLE ONLY governance."meetings_2bDeleted"
    ADD CONSTRAINT "meetings_pkey_2bDeleted" PRIMARY KEY (dor, authority, date);


--
-- Name: grid grid_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.grid
    ADD CONSTRAINT grid_pkey PRIMARY KEY (circuit_id);


--
-- Name: schools_types school_types_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.schools_types
    ADD CONSTRAINT school_types_pkey PRIMARY KEY (dor, schools_type, year);


--
-- Name: schools_enrollment schools_enrollment_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.schools_enrollment
    ADD CONSTRAINT schools_enrollment_pkey PRIMARY KEY (school_id, year, grade);


--
-- Name: schools_mcas schools_mcas_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.schools_mcas
    ADD CONSTRAINT schools_mcas_pkey PRIMARY KEY (school_id, year, mcas_subject, mcas_grade, mcas);


--
-- Name: schools_nss schools_nss_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.schools_nss
    ADD CONSTRAINT schools_nss_pkey PRIMARY KEY (school_id, year, nss);


--
-- Name: schools_ppx schools_ppx_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.schools_ppx
    ADD CONSTRAINT schools_ppx_pkey PRIMARY KEY (school_id, year, ppx);


--
-- Name: schools_teacher_age schools_teacher_age_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.schools_teacher_age
    ADD CONSTRAINT schools_teacher_age_pkey PRIMARY KEY (school_id, year, teacher_age);


--
-- Name: schools_teacher_program_area schools_teacher_program_area_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.schools_teacher_program_area
    ADD CONSTRAINT schools_teacher_program_area_pkey PRIMARY KEY (school_id, year, teacher_program_area);


--
-- Name: schools_teacher_race schools_teacher_race_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.schools_teacher_race
    ADD CONSTRAINT schools_teacher_race_pkey PRIMARY KEY (school_id, year, teacher_race);


--
-- Name: schools_teacher_salaries schools_teacher_salaries_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.schools_teacher_salaries
    ADD CONSTRAINT schools_teacher_salaries_pkey PRIMARY KEY (school_id, year, teacher_salaries);


--
-- Name: water_accounts water_accounts_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.water_accounts
    ADD CONSTRAINT water_accounts_pkey PRIMARY KEY (account, date);


--
-- Name: water_bills water_bills_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.water_bills
    ADD CONSTRAINT water_bills_pkey PRIMARY KEY (account, date);


--
-- Name: addresses addresses_pkey; Type: CONSTRAINT; Schema: people; Owner: -
--

ALTER TABLE ONLY people.addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (address_id);


--
-- Name: attributes attributes_pkey; Type: CONSTRAINT; Schema: people; Owner: -
--

ALTER TABLE ONLY people.attributes
    ADD CONSTRAINT attributes_pkey PRIMARY KEY (people_id);


--
-- Name: elections elections_pkey; Type: CONSTRAINT; Schema: people; Owner: -
--

ALTER TABLE ONLY people.elections
    ADD CONSTRAINT elections_pkey PRIMARY KEY (people_id);


--
-- Name: registered registered_pkey; Type: CONSTRAINT; Schema: people; Owner: -
--

ALTER TABLE ONLY people.registered
    ADD CONSTRAINT registered_pkey PRIMARY KEY (people_id);


--
-- Name: residents residents_pkey; Type: CONSTRAINT; Schema: people; Owner: -
--

ALTER TABLE ONLY people.residents
    ADD CONSTRAINT residents_pkey PRIMARY KEY (people_id);


--
-- Name: assessments assessments_pkey1; Type: CONSTRAINT; Schema: property; Owner: -
--

ALTER TABLE ONLY property.assessments
    ADD CONSTRAINT assessments_pkey1 PRIMARY KEY (year, loc_id2, pid);


--
-- Name: deeds_parcel_xref deeds_parcel_xref_pkey; Type: CONSTRAINT; Schema: property; Owner: -
--

ALTER TABLE ONLY property.deeds_parcel_xref
    ADD CONSTRAINT deeds_parcel_xref_pkey PRIMARY KEY (date, docno);


--
-- Name: mbta_districts mbta_pkey; Type: CONSTRAINT; Schema: property; Owner: -
--

ALTER TABLE ONLY property.mbta_districts
    ADD CONSTRAINT mbta_pkey PRIMARY KEY (pid);


--
-- Name: patriot patriot_account_key; Type: CONSTRAINT; Schema: property; Owner: -
--

ALTER TABLE ONLY property.patriot
    ADD CONSTRAINT patriot_account_key UNIQUE (account);


--
-- Name: patriot_int_value_pairs patriot_int_value_pairs_pkey; Type: CONSTRAINT; Schema: property; Owner: -
--

ALTER TABLE ONLY property.patriot_int_value_pairs
    ADD CONSTRAINT patriot_int_value_pairs_pkey PRIMARY KEY (item, key);


--
-- Name: patriot patriot_pkey; Type: CONSTRAINT; Schema: property; Owner: -
--

ALTER TABLE ONLY property.patriot
    ADD CONSTRAINT patriot_pkey PRIMARY KEY (year, account, pid);


--
-- Name: patriot_summary patriot_summary_pkey; Type: CONSTRAINT; Schema: property; Owner: -
--

ALTER TABLE ONLY property.patriot_summary
    ADD CONSTRAINT patriot_summary_pkey PRIMARY KEY (fy, parcel);


--
-- Name: permits permits_pkey; Type: CONSTRAINT; Schema: property; Owner: -
--

ALTER TABLE ONLY property.permits
    ADD CONSTRAINT permits_pkey PRIMARY KEY (date, permit_type, permit);


--
-- Name: common_structures_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX common_structures_idx ON common.structures USING btree (pid);


--
-- Name: common_structures_struct_id_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX common_structures_struct_id_idx ON common.structures USING btree (struct_id);


--
-- Name: int_value_pairs_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX int_value_pairs_idx ON common.int_value_pairs USING btree (key);


--
-- Name: int_value_pairs_item_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX int_value_pairs_item_idx ON common.int_value_pairs USING btree (item);


--
-- Name: loc_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX loc_idx ON common.loc_pid_address USING btree (loc_id);


--
-- Name: loc_pid_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX loc_pid_idx ON common.loc_pid USING btree (loc_id);


--
-- Name: loc_pid_pid_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX loc_pid_pid_idx ON common.loc_pid USING btree (pid);


--
-- Name: naics_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX naics_idx ON common.naics USING btree (key);


--
-- Name: pid_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX pid_idx ON common.loc_pid_address USING btree (pid);


--
-- Name: polygons_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX polygons_idx ON common.loc_polygons USING btree (loc_id);


--
-- Name: school_id_location_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX school_id_location_idx ON common.school_id_location USING btree (school_id);


--
-- Name: town_boundaries_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX town_boundaries_idx ON common.town_boundaries USING btree (town_id);


--
-- Name: town_boundaries_town_idx; Type: INDEX; Schema: common; Owner: -
--

CREATE INDEX town_boundaries_town_idx ON common.town_boundaries USING btree (town);


--
-- Name: eia_generator_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_generator_idx ON energy.eia_generator USING btree (plant_code);


--
-- Name: eia_generator_ownership_generator_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_generator_ownership_generator_idx ON energy.eia_generator_ownership USING btree (generator_id);


--
-- Name: eia_generator_ownership_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_generator_ownership_idx ON energy.eia_generator_ownership USING btree (plant_code);


--
-- Name: eia_generator_ownership_owner_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_generator_ownership_owner_idx ON energy.eia_generator_ownership USING btree (owner_id);


--
-- Name: eia_generator_ownership_utility_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_generator_ownership_utility_idx ON energy.eia_generator_ownership USING btree (utility_id);


--
-- Name: eia_generator_utility_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_generator_utility_idx ON energy.eia_generator USING btree (utility_id);


--
-- Name: eia_multifuel_generator_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_multifuel_generator_idx ON energy.eia_multifuel USING btree (generator_id);


--
-- Name: eia_multifuel_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_multifuel_idx ON energy.eia_multifuel USING btree (plant_code);


--
-- Name: eia_multifuel_utility_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_multifuel_utility_idx ON energy.eia_multifuel USING btree (utility_id);


--
-- Name: eia_plant_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_plant_idx ON energy.eia_plant USING btree (plant_code);


--
-- Name: eia_plant_utility_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_plant_utility_idx ON energy.eia_plant USING btree (utility_id);


--
-- Name: eia_solar_generator_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_solar_generator_idx ON energy.eia_solar USING btree (generator_id);


--
-- Name: eia_solar_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_solar_idx ON energy.eia_solar USING btree (plant_code);


--
-- Name: eia_solar_utility_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_solar_utility_idx ON energy.eia_solar USING btree (utility_id);


--
-- Name: eia_storage_generator_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_storage_generator_idx ON energy.eia_storage USING btree (generator_id);


--
-- Name: eia_storage_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_storage_idx ON energy.eia_storage USING btree (plant_code);


--
-- Name: eia_storage_utility_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_storage_utility_idx ON energy.eia_storage USING btree (utility_id);


--
-- Name: eia_utility_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_utility_idx ON energy.eia_utility USING btree (utility_id);


--
-- Name: eia_wind_generator_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_wind_generator_idx ON energy.eia_wind USING btree (generator_id);


--
-- Name: eia_wind_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_wind_idx ON energy.eia_wind USING btree (plant_code);


--
-- Name: eia_wind_utility_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX eia_wind_utility_idx ON energy.eia_wind USING btree (utility_id);


--
-- Name: energy_solar_date_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX energy_solar_date_idx ON energy.solar USING btree (date);


--
-- Name: energy_solar_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX energy_solar_idx ON energy.solar USING btree (pid);


--
-- Name: energy_solar_pid_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX energy_solar_pid_idx ON energy.solar USING btree (pid);


--
-- Name: iso_genfuelmix_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX iso_genfuelmix_idx ON energy.iso_genfuelmix USING btree (iso_fuel, datetime);


--
-- Name: iso_lmp_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX iso_lmp_idx ON energy.iso_lmp USING btree (location_id);


--
-- Name: iso_lmp_idx_dt; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX iso_lmp_idx_dt ON energy.iso_lmp USING btree (datetime);


--
-- Name: iso_system_loads_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX iso_system_loads_idx ON energy.iso_system_loads USING btree (datetime);


--
-- Name: solar_bnl_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX solar_bnl_idx ON energy.solar_bnl USING btree (dor);


--
-- Name: solar_bnl_idx_date; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX solar_bnl_idx_date ON energy.solar_bnl USING btree (date);


--
-- Name: solar_pts_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX solar_pts_idx ON energy.solar_pts USING btree (dor);


--
-- Name: solar_pts_idx_year; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX solar_pts_idx_year ON energy.solar_pts USING btree (year);


--
-- Name: solar_rps_idx; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX solar_rps_idx ON energy.solar_rps USING btree (dor);


--
-- Name: solar_rps_idx_date; Type: INDEX; Schema: energy; Owner: -
--

CREATE INDEX solar_rps_idx_date ON energy.solar_rps USING btree (date);


--
-- Name: checkbook_department_idx; Type: INDEX; Schema: governance; Owner: -
--

CREATE INDEX checkbook_department_idx ON governance.checkbook USING btree (checkbook_department);


--
-- Name: governance_checkbook_idx; Type: INDEX; Schema: governance; Owner: -
--

CREATE INDEX governance_checkbook_idx ON governance.checkbook USING btree (date);


--
-- Name: governance_meetings_date_idx_2bDeleted; Type: INDEX; Schema: governance; Owner: -
--

CREATE INDEX "governance_meetings_date_idx_2bDeleted" ON governance."meetings_2bDeleted" USING btree (dor, date);


--
-- Name: governance_meetings_directory_date_idx; Type: INDEX; Schema: governance; Owner: -
--

CREATE INDEX governance_meetings_directory_date_idx ON governance.meetings_directory USING btree (dor, date);


--
-- Name: governance_meetings_directory_idx; Type: INDEX; Schema: governance; Owner: -
--

CREATE INDEX governance_meetings_directory_idx ON governance.meetings_directory USING btree (dor, authority);


--
-- Name: governance_meetings_idx_2bDeleted; Type: INDEX; Schema: governance; Owner: -
--

CREATE INDEX "governance_meetings_idx_2bDeleted" ON governance."meetings_2bDeleted" USING btree (dor, authority);


--
-- Name: tmm_precinct_idx; Type: INDEX; Schema: governance; Owner: -
--

CREATE INDEX tmm_precinct_idx ON governance.tmm USING btree (precinct);


--
-- Name: tmm_year_idx; Type: INDEX; Schema: governance; Owner: -
--

CREATE INDEX tmm_year_idx ON governance.tmm USING btree (year);


--
-- Name: grid_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX grid_idx ON infrastructure.grid USING btree (circuit_id);


--
-- Name: grid_segments_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX grid_segments_idx ON infrastructure.grid_segments USING btree (circuit_id);


--
-- Name: ppp_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX ppp_idx ON infrastructure.ppp USING btree (pid);


--
-- Name: road_segments_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX road_segments_idx ON infrastructure.road_segments USING btree (class);


--
-- Name: roads_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX roads_idx ON infrastructure.roads USING btree (class);


--
-- Name: school_type_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX school_type_idx ON infrastructure.schools_types USING btree (schools_type);


--
-- Name: schools_enrollment_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_enrollment_idx ON infrastructure.schools_enrollment USING btree (school_id);


--
-- Name: schools_enrollment_year_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_enrollment_year_idx ON infrastructure.schools_enrollment USING btree (year);


--
-- Name: schools_mcas_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_mcas_idx ON infrastructure.schools_mcas USING btree (school_id);


--
-- Name: schools_mcas_year_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_mcas_year_idx ON infrastructure.schools_mcas USING btree (year);


--
-- Name: schools_nss_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_nss_idx ON infrastructure.schools_nss USING btree (school_id);


--
-- Name: schools_nss_year_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_nss_year_idx ON infrastructure.schools_nss USING btree (year);


--
-- Name: schools_ppx_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_ppx_idx ON infrastructure.schools_ppx USING btree (school_id);


--
-- Name: schools_ppx_year_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_ppx_year_idx ON infrastructure.schools_ppx USING btree (year);


--
-- Name: schools_teacher_age_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_teacher_age_idx ON infrastructure.schools_teacher_age USING btree (school_id);


--
-- Name: schools_teacher_age_year_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_teacher_age_year_idx ON infrastructure.schools_teacher_age USING btree (year);


--
-- Name: schools_teacher_program_area_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_teacher_program_area_idx ON infrastructure.schools_teacher_program_area USING btree (school_id);


--
-- Name: schools_teacher_program_area_year_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_teacher_program_area_year_idx ON infrastructure.schools_teacher_program_area USING btree (year);


--
-- Name: schools_teacher_race_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_teacher_race_idx ON infrastructure.schools_teacher_race USING btree (school_id);


--
-- Name: schools_teacher_race_year_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_teacher_race_year_idx ON infrastructure.schools_teacher_race USING btree (year);


--
-- Name: schools_teacher_salaries_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_teacher_salaries_idx ON infrastructure.schools_teacher_salaries USING btree (school_id);


--
-- Name: schools_teacher_salaries_year_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX schools_teacher_salaries_year_idx ON infrastructure.schools_teacher_salaries USING btree (year);


--
-- Name: water_accounts_account_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX water_accounts_account_idx ON infrastructure.water_accounts USING btree (pid);


--
-- Name: water_bills_account_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX water_bills_account_idx ON infrastructure.water_bills USING btree (account);


--
-- Name: water_bills_date_idx; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX water_bills_date_idx ON infrastructure.water_bills USING btree (date);


--
-- Name: addresses_idx; Type: INDEX; Schema: people; Owner: -
--

CREATE INDEX addresses_idx ON people.addresses USING btree (address_id);


--
-- Name: attributes_idx; Type: INDEX; Schema: people; Owner: -
--

CREATE INDEX attributes_idx ON people.attributes USING btree (people_id);


--
-- Name: elections_idx; Type: INDEX; Schema: people; Owner: -
--

CREATE INDEX elections_idx ON people.elections USING btree (people_id);


--
-- Name: people_activity_type_histogram_idx; Type: INDEX; Schema: people; Owner: -
--

CREATE INDEX people_activity_type_histogram_idx ON people.activity_type_histogram USING btree (date);


--
-- Name: people_party_histogram_idx; Type: INDEX; Schema: people; Owner: -
--

CREATE INDEX people_party_histogram_idx ON people.party_histogram USING btree (date);


--
-- Name: people_precinct_histogram_idx; Type: INDEX; Schema: people; Owner: -
--

CREATE INDEX people_precinct_histogram_idx ON people.precinct_histogram USING btree (date);


--
-- Name: people_sex_histogram_idx; Type: INDEX; Schema: people; Owner: -
--

CREATE INDEX people_sex_histogram_idx ON people.sex_histogram USING btree (date);


--
-- Name: registered_idx; Type: INDEX; Schema: people; Owner: -
--

CREATE INDEX registered_idx ON people.registered USING btree (people_id);


--
-- Name: residents_idx; Type: INDEX; Schema: people; Owner: -
--

CREATE INDEX residents_idx ON people.residents USING btree (people_id);


--
-- Name: assessments_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX assessments_idx ON property.assessments USING btree (pid);


--
-- Name: deeds_details_bp_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX deeds_details_bp_idx ON property.deeds_details USING btree (book, page);


--
-- Name: deeds_details_deeds_details_mtgdeed_only_bp_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX deeds_details_deeds_details_mtgdeed_only_bp_idx ON property.deeds_details USING btree (book, page);


--
-- Name: deeds_details_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX deeds_details_idx ON property.deeds_details USING btree (docno);


--
-- Name: deeds_details_raw_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX deeds_details_raw_idx ON property.deeds_details_raw USING btree ("Doc. #");


--
-- Name: deeds_details_raw_idx_2bDeleted; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX "deeds_details_raw_idx_2bDeleted" ON property."deeds_details_raw_2bDeleted" USING btree ("Doc. #");


--
-- Name: deeds_parcel_xref_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX deeds_parcel_xref_idx ON property.deeds_parcel_xref USING btree (bookpage);


--
-- Name: deeds_summary_date_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX deeds_summary_date_idx ON property.deeds_summary USING btree (date);


--
-- Name: deeds_summary_deed_type_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX deeds_summary_deed_type_idx ON property.deeds_summary USING btree (deed_type);


--
-- Name: deeds_summary_docno_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX deeds_summary_docno_idx ON property.deeds_summary USING btree (docno);


--
-- Name: deeds_summary_town_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX deeds_summary_town_idx ON property.deeds_summary USING btree (town);


--
-- Name: heatpumps_date_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX heatpumps_date_idx ON property.heatpumps USING btree (installed);


--
-- Name: heatpumps_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX heatpumps_idx ON property.heatpumps USING btree (pid);


--
-- Name: patriot_int_value_pairs_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX patriot_int_value_pairs_idx ON property.patriot_int_value_pairs USING btree (item);


--
-- Name: patriot_parcel_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX patriot_parcel_idx ON property.patriot USING btree (pid);


--
-- Name: patriot_parcel_year_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX patriot_parcel_year_idx ON property.patriot USING btree (year);


--
-- Name: patriot_summary_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX patriot_summary_idx ON property.patriot_summary USING btree (parcel);


--
-- Name: permits_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX permits_idx ON property.permits USING btree (pid);


--
-- Name: permits_year_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX permits_year_idx ON property.permits USING btree (year);


--
-- Name: sales_idx; Type: INDEX; Schema: property; Owner: -
--

CREATE INDEX sales_idx ON property.sales USING btree (pid);


--
-- Name: SCHEMA common; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA common TO PUBLIC;


--
-- Name: SCHEMA governance; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA governance TO PUBLIC;


--
-- Name: SCHEMA infrastructure; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA infrastructure TO PUBLIC;


--
-- Name: SCHEMA people; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA people TO PUBLIC;


--
-- Name: SCHEMA property; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA property TO PUBLIC;


--
-- PostgreSQL database dump complete
--

