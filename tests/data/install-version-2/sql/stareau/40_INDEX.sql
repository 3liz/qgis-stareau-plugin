--
-- PostgreSQL database dump
--






SET statement_timeout = 0;
SET lock_timeout = 0;


SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

-- stareau_aep_edge_geom_idx
CREATE INDEX stareau_aep_edge_geom_idx ON stareau.aep_edge USING gist (geom);


-- stareau_aep_vertex_geom_idx
CREATE INDEX stareau_aep_vertex_geom_idx ON stareau.aep_vertex USING gist (geom);


--
-- PostgreSQL database dump complete
--



