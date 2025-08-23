--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.9

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
-- Name: public; Type: SCHEMA; Schema: -; Owner: appuser
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO appuser;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: appuser
--

COMMENT ON SCHEMA public IS '';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: appuser
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO appuser;

--
-- Name: blank_templates; Type: TABLE; Schema: public; Owner: appuser
--

CREATE TABLE public.blank_templates (
    template_id integer NOT NULL,
    template_name character varying(128) NOT NULL,
    file_id character varying(64) NOT NULL,
    description text,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.blank_templates OWNER TO appuser;

--
-- Name: blank_templates_template_id_seq; Type: SEQUENCE; Schema: public; Owner: appuser
--

CREATE SEQUENCE public.blank_templates_template_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.blank_templates_template_id_seq OWNER TO appuser;

--
-- Name: blank_templates_template_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: appuser
--

ALTER SEQUENCE public.blank_templates_template_id_seq OWNED BY public.blank_templates.template_id;


--
-- Name: budget_items; Type: TABLE; Schema: public; Owner: appuser
--

CREATE TABLE public.budget_items (
    item_id integer NOT NULL,
    budget_id character varying(64) NOT NULL,
    name character varying(255) NOT NULL,
    type character varying(32) NOT NULL,
    unit character varying(32),
    quantity double precision,
    unit_price double precision,
    total_price double precision,
    description text,
    metadata json
);


ALTER TABLE public.budget_items OWNER TO appuser;

--
-- Name: budget_items_item_id_seq; Type: SEQUENCE; Schema: public; Owner: appuser
--

CREATE SEQUENCE public.budget_items_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.budget_items_item_id_seq OWNER TO appuser;

--
-- Name: budget_items_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: appuser
--

ALTER SEQUENCE public.budget_items_item_id_seq OWNED BY public.budget_items.item_id;


--
-- Name: generated_forms; Type: TABLE; Schema: public; Owner: appuser
--

CREATE TABLE public.generated_forms (
    form_id integer NOT NULL,
    temp_file_id integer NOT NULL,
    template_id integer NOT NULL,
    form_name character varying(255) NOT NULL,
    creation_date timestamp without time zone NOT NULL,
    file_id character varying(64) NOT NULL,
    file_format character varying(16) NOT NULL,
    metadata json
);


ALTER TABLE public.generated_forms OWNER TO appuser;

--
-- Name: generated_forms_form_id_seq; Type: SEQUENCE; Schema: public; Owner: appuser
--

CREATE SEQUENCE public.generated_forms_form_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.generated_forms_form_id_seq OWNER TO appuser;

--
-- Name: generated_forms_form_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: appuser
--

ALTER SEQUENCE public.generated_forms_form_id_seq OWNED BY public.generated_forms.form_id;


--
-- Name: quality_standards; Type: TABLE; Schema: public; Owner: appuser
--

CREATE TABLE public.quality_standards (
    standard_id integer NOT NULL,
    item_name character varying(255) NOT NULL,
    item_type character varying(32) NOT NULL,
    source character varying(255),
    inspection_items json,
    inspection_methods json,
    acceptance_criteria json,
    frequency character varying(128),
    responsible_party character varying(128),
    notes text,
    metadata json
);


ALTER TABLE public.quality_standards OWNER TO appuser;

--
-- Name: quality_standards_standard_id_seq; Type: SEQUENCE; Schema: public; Owner: appuser
--

CREATE SEQUENCE public.quality_standards_standard_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quality_standards_standard_id_seq OWNER TO appuser;

--
-- Name: quality_standards_standard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: appuser
--

ALTER SEQUENCE public.quality_standards_standard_id_seq OWNED BY public.quality_standards.standard_id;


--
-- Name: reference_files; Type: TABLE; Schema: public; Owner: appuser
--

CREATE TABLE public.reference_files (
    id integer NOT NULL,
    category character varying(32) NOT NULL,
    description text,
    file_id character varying(64) NOT NULL,
    project_name character varying(128),
    created_at timestamp without time zone NOT NULL,
    metadata json
);


ALTER TABLE public.reference_files OWNER TO appuser;

--
-- Name: reference_files_id_seq; Type: SEQUENCE; Schema: public; Owner: appuser
--

CREATE SEQUENCE public.reference_files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reference_files_id_seq OWNER TO appuser;

--
-- Name: reference_files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: appuser
--

ALTER SEQUENCE public.reference_files_id_seq OWNED BY public.reference_files.id;


--
-- Name: spec_items; Type: TABLE; Schema: public; Owner: appuser
--

CREATE TABLE public.spec_items (
    id integer NOT NULL,
    spec_id character varying(64) NOT NULL,
    item_name character varying(255) NOT NULL,
    item_type character varying(32),
    requirements json,
    standards json,
    testing_methods json,
    acceptance_criteria json,
    notes text,
    metadata json
);


ALTER TABLE public.spec_items OWNER TO appuser;

--
-- Name: spec_items_id_seq; Type: SEQUENCE; Schema: public; Owner: appuser
--

CREATE SEQUENCE public.spec_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.spec_items_id_seq OWNER TO appuser;

--
-- Name: spec_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: appuser
--

ALTER SEQUENCE public.spec_items_id_seq OWNED BY public.spec_items.id;


--
-- Name: stored_files; Type: TABLE; Schema: public; Owner: appuser
--

CREATE TABLE public.stored_files (
    file_id integer NOT NULL,
    original_name character varying(255) NOT NULL,
    stored_path character varying(512) NOT NULL,
    mime_type character varying(128),
    size_bytes integer,
    created_at timestamp without time zone NOT NULL,
    metadata json
);


ALTER TABLE public.stored_files OWNER TO appuser;

--
-- Name: stored_files_file_id_seq; Type: SEQUENCE; Schema: public; Owner: appuser
--

CREATE SEQUENCE public.stored_files_file_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stored_files_file_id_seq OWNER TO appuser;

--
-- Name: stored_files_file_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: appuser
--

ALTER SEQUENCE public.stored_files_file_id_seq OWNED BY public.stored_files.file_id;


--
-- Name: temp_standard_files; Type: TABLE; Schema: public; Owner: appuser
--

CREATE TABLE public.temp_standard_files (
    temp_file_id integer NOT NULL,
    budget_id character varying(64) NOT NULL,
    spec_id character varying(64),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.temp_standard_files OWNER TO appuser;

--
-- Name: temp_standard_files_temp_file_id_seq; Type: SEQUENCE; Schema: public; Owner: appuser
--

CREATE SEQUENCE public.temp_standard_files_temp_file_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.temp_standard_files_temp_file_id_seq OWNER TO appuser;

--
-- Name: temp_standard_files_temp_file_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: appuser
--

ALTER SEQUENCE public.temp_standard_files_temp_file_id_seq OWNED BY public.temp_standard_files.temp_file_id;


--
-- Name: temp_standard_items; Type: TABLE; Schema: public; Owner: appuser
--

CREATE TABLE public.temp_standard_items (
    temp_item_id integer NOT NULL,
    temp_file_id integer NOT NULL,
    budget_item_id integer NOT NULL,
    item_name character varying(255) NOT NULL,
    item_type character varying(32) NOT NULL,
    reference_standard_id integer,
    inspection_items json,
    inspection_methods json,
    acceptance_criteria json,
    frequency character varying(128),
    responsible_party character varying(128),
    notes text,
    is_modified boolean NOT NULL,
    last_modified timestamp without time zone NOT NULL,
    metadata json
);


ALTER TABLE public.temp_standard_items OWNER TO appuser;

--
-- Name: temp_standard_items_temp_item_id_seq; Type: SEQUENCE; Schema: public; Owner: appuser
--

CREATE SEQUENCE public.temp_standard_items_temp_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.temp_standard_items_temp_item_id_seq OWNER TO appuser;

--
-- Name: temp_standard_items_temp_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: appuser
--

ALTER SEQUENCE public.temp_standard_items_temp_item_id_seq OWNED BY public.temp_standard_items.temp_item_id;


--
-- Name: blank_templates template_id; Type: DEFAULT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.blank_templates ALTER COLUMN template_id SET DEFAULT nextval('public.blank_templates_template_id_seq'::regclass);


--
-- Name: budget_items item_id; Type: DEFAULT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.budget_items ALTER COLUMN item_id SET DEFAULT nextval('public.budget_items_item_id_seq'::regclass);


--
-- Name: generated_forms form_id; Type: DEFAULT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.generated_forms ALTER COLUMN form_id SET DEFAULT nextval('public.generated_forms_form_id_seq'::regclass);


--
-- Name: quality_standards standard_id; Type: DEFAULT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.quality_standards ALTER COLUMN standard_id SET DEFAULT nextval('public.quality_standards_standard_id_seq'::regclass);


--
-- Name: reference_files id; Type: DEFAULT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.reference_files ALTER COLUMN id SET DEFAULT nextval('public.reference_files_id_seq'::regclass);


--
-- Name: spec_items id; Type: DEFAULT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.spec_items ALTER COLUMN id SET DEFAULT nextval('public.spec_items_id_seq'::regclass);


--
-- Name: stored_files file_id; Type: DEFAULT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.stored_files ALTER COLUMN file_id SET DEFAULT nextval('public.stored_files_file_id_seq'::regclass);


--
-- Name: temp_standard_files temp_file_id; Type: DEFAULT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.temp_standard_files ALTER COLUMN temp_file_id SET DEFAULT nextval('public.temp_standard_files_temp_file_id_seq'::regclass);


--
-- Name: temp_standard_items temp_item_id; Type: DEFAULT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.temp_standard_items ALTER COLUMN temp_item_id SET DEFAULT nextval('public.temp_standard_items_temp_item_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: appuser
--

COPY public.alembic_version (version_num) FROM stdin;
13ec7739de7d
\.


--
-- Data for Name: blank_templates; Type: TABLE DATA; Schema: public; Owner: appuser
--

COPY public.blank_templates (template_id, template_name, file_id, description, created_at) FROM stdin;
\.


--
-- Data for Name: budget_items; Type: TABLE DATA; Schema: public; Owner: appuser
--

COPY public.budget_items (item_id, budget_id, name, type, unit, quantity, unit_price, total_price, description, metadata) FROM stdin;
\.


--
-- Data for Name: generated_forms; Type: TABLE DATA; Schema: public; Owner: appuser
--

COPY public.generated_forms (form_id, temp_file_id, template_id, form_name, creation_date, file_id, file_format, metadata) FROM stdin;
\.


--
-- Data for Name: quality_standards; Type: TABLE DATA; Schema: public; Owner: appuser
--

COPY public.quality_standards (standard_id, item_name, item_type, source, inspection_items, inspection_methods, acceptance_criteria, frequency, responsible_party, notes, metadata) FROM stdin;
\.


--
-- Data for Name: reference_files; Type: TABLE DATA; Schema: public; Owner: appuser
--

COPY public.reference_files (id, category, description, file_id, project_name, created_at, metadata) FROM stdin;
\.


--
-- Data for Name: spec_items; Type: TABLE DATA; Schema: public; Owner: appuser
--

COPY public.spec_items (id, spec_id, item_name, item_type, requirements, standards, testing_methods, acceptance_criteria, notes, metadata) FROM stdin;
\.


--
-- Data for Name: stored_files; Type: TABLE DATA; Schema: public; Owner: appuser
--

COPY public.stored_files (file_id, original_name, stored_path, mime_type, size_bytes, created_at, metadata) FROM stdin;
\.


--
-- Data for Name: temp_standard_files; Type: TABLE DATA; Schema: public; Owner: appuser
--

COPY public.temp_standard_files (temp_file_id, budget_id, spec_id, created_at) FROM stdin;
\.


--
-- Data for Name: temp_standard_items; Type: TABLE DATA; Schema: public; Owner: appuser
--

COPY public.temp_standard_items (temp_item_id, temp_file_id, budget_item_id, item_name, item_type, reference_standard_id, inspection_items, inspection_methods, acceptance_criteria, frequency, responsible_party, notes, is_modified, last_modified, metadata) FROM stdin;
\.


--
-- Name: blank_templates_template_id_seq; Type: SEQUENCE SET; Schema: public; Owner: appuser
--

SELECT pg_catalog.setval('public.blank_templates_template_id_seq', 1, false);


--
-- Name: budget_items_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: appuser
--

SELECT pg_catalog.setval('public.budget_items_item_id_seq', 1, false);


--
-- Name: generated_forms_form_id_seq; Type: SEQUENCE SET; Schema: public; Owner: appuser
--

SELECT pg_catalog.setval('public.generated_forms_form_id_seq', 1, false);


--
-- Name: quality_standards_standard_id_seq; Type: SEQUENCE SET; Schema: public; Owner: appuser
--

SELECT pg_catalog.setval('public.quality_standards_standard_id_seq', 1, false);


--
-- Name: reference_files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: appuser
--

SELECT pg_catalog.setval('public.reference_files_id_seq', 1, false);


--
-- Name: spec_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: appuser
--

SELECT pg_catalog.setval('public.spec_items_id_seq', 1, false);


--
-- Name: stored_files_file_id_seq; Type: SEQUENCE SET; Schema: public; Owner: appuser
--

SELECT pg_catalog.setval('public.stored_files_file_id_seq', 1, false);


--
-- Name: temp_standard_files_temp_file_id_seq; Type: SEQUENCE SET; Schema: public; Owner: appuser
--

SELECT pg_catalog.setval('public.temp_standard_files_temp_file_id_seq', 1, false);


--
-- Name: temp_standard_items_temp_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: appuser
--

SELECT pg_catalog.setval('public.temp_standard_items_temp_item_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: blank_templates pk_blank_templates; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.blank_templates
    ADD CONSTRAINT pk_blank_templates PRIMARY KEY (template_id);


--
-- Name: budget_items pk_budget_items; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.budget_items
    ADD CONSTRAINT pk_budget_items PRIMARY KEY (item_id);


--
-- Name: generated_forms pk_generated_forms; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.generated_forms
    ADD CONSTRAINT pk_generated_forms PRIMARY KEY (form_id);


--
-- Name: quality_standards pk_quality_standards; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.quality_standards
    ADD CONSTRAINT pk_quality_standards PRIMARY KEY (standard_id);


--
-- Name: reference_files pk_reference_files; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.reference_files
    ADD CONSTRAINT pk_reference_files PRIMARY KEY (id);


--
-- Name: spec_items pk_spec_items; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.spec_items
    ADD CONSTRAINT pk_spec_items PRIMARY KEY (id);


--
-- Name: stored_files pk_stored_files; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.stored_files
    ADD CONSTRAINT pk_stored_files PRIMARY KEY (file_id);


--
-- Name: temp_standard_files pk_temp_standard_files; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.temp_standard_files
    ADD CONSTRAINT pk_temp_standard_files PRIMARY KEY (temp_file_id);


--
-- Name: temp_standard_items pk_temp_standard_items; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.temp_standard_items
    ADD CONSTRAINT pk_temp_standard_items PRIMARY KEY (temp_item_id);


--
-- Name: ix_blank_templates_file_id; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_blank_templates_file_id ON public.blank_templates USING btree (file_id);


--
-- Name: ix_blank_templates_template_name; Type: INDEX; Schema: public; Owner: appuser
--

CREATE UNIQUE INDEX ix_blank_templates_template_name ON public.blank_templates USING btree (template_name);


--
-- Name: ix_budget_items_budget_id; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_budget_items_budget_id ON public.budget_items USING btree (budget_id);


--
-- Name: ix_budget_items_name; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_budget_items_name ON public.budget_items USING btree (name);


--
-- Name: ix_budget_items_name_type; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_budget_items_name_type ON public.budget_items USING btree (name, type);


--
-- Name: ix_generated_forms_file_id; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_generated_forms_file_id ON public.generated_forms USING btree (file_id);


--
-- Name: ix_generated_forms_form_name; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_generated_forms_form_name ON public.generated_forms USING btree (form_name);


--
-- Name: ix_quality_standards_item; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_quality_standards_item ON public.quality_standards USING btree (item_name, item_type);


--
-- Name: ix_quality_standards_item_name; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_quality_standards_item_name ON public.quality_standards USING btree (item_name);


--
-- Name: ix_quality_standards_item_type; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_quality_standards_item_type ON public.quality_standards USING btree (item_type);


--
-- Name: ix_reference_files_file_id; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_reference_files_file_id ON public.reference_files USING btree (file_id);


--
-- Name: ix_spec_items_item_name; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_spec_items_item_name ON public.spec_items USING btree (item_name);


--
-- Name: ix_spec_items_spec_id; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_spec_items_spec_id ON public.spec_items USING btree (spec_id);


--
-- Name: ix_temp_standard_files_budget_id; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_temp_standard_files_budget_id ON public.temp_standard_files USING btree (budget_id);


--
-- Name: ix_temp_standard_files_spec_id; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_temp_standard_files_spec_id ON public.temp_standard_files USING btree (spec_id);


--
-- Name: ix_temp_standard_items_item_name; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_temp_standard_items_item_name ON public.temp_standard_items USING btree (item_name);


--
-- Name: ix_temp_standard_items_item_type; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX ix_temp_standard_items_item_type ON public.temp_standard_items USING btree (item_type);


--
-- Name: generated_forms fk_generated_forms_temp_file_id_temp_standard_files; Type: FK CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.generated_forms
    ADD CONSTRAINT fk_generated_forms_temp_file_id_temp_standard_files FOREIGN KEY (temp_file_id) REFERENCES public.temp_standard_files(temp_file_id);


--
-- Name: generated_forms fk_generated_forms_template_id_blank_templates; Type: FK CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.generated_forms
    ADD CONSTRAINT fk_generated_forms_template_id_blank_templates FOREIGN KEY (template_id) REFERENCES public.blank_templates(template_id);


--
-- Name: temp_standard_items fk_temp_standard_items_budget_item_id_budget_items; Type: FK CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.temp_standard_items
    ADD CONSTRAINT fk_temp_standard_items_budget_item_id_budget_items FOREIGN KEY (budget_item_id) REFERENCES public.budget_items(item_id);


--
-- Name: temp_standard_items fk_temp_standard_items_reference_standard_id_quality_standards; Type: FK CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.temp_standard_items
    ADD CONSTRAINT fk_temp_standard_items_reference_standard_id_quality_standards FOREIGN KEY (reference_standard_id) REFERENCES public.quality_standards(standard_id);


--
-- Name: temp_standard_items fk_temp_standard_items_temp_file_id_temp_standard_files; Type: FK CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.temp_standard_items
    ADD CONSTRAINT fk_temp_standard_items_temp_file_id_temp_standard_files FOREIGN KEY (temp_file_id) REFERENCES public.temp_standard_files(temp_file_id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: appuser
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

