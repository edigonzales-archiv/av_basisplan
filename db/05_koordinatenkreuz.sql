-- Table: av_basisplan.koordinatenkreuz

-- DROP TABLE av_basisplan.koordinatenkreuz;

CREATE TABLE av_basisplan.koordinatenkreuz
(
  ogc_fid serial NOT NULL,
  abstand integer,
  pos geometry,
  CONSTRAINT koordinatenkreuz_pkey PRIMARY KEY (ogc_fid),
  CONSTRAINT enforce_dims_pos CHECK (st_ndims(pos) = 2),
  CONSTRAINT enforce_geotype_pos CHECK (geometrytype(pos) = 'POINT'::text OR pos IS NULL),
  CONSTRAINT enforce_srid_pos CHECK (st_srid(pos) = 21781)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE av_basisplan.koordinatenkreuz OWNER TO stefan;
GRANT ALL ON TABLE av_basisplan.koordinatenkreuz TO stefan;
GRANT SELECT ON TABLE av_basisplan.koordinatenkreuz TO mspublic;


CREATE INDEX idx_av_basisplan.koordinatenkreuz_pos
  ON av_basisplan.koordinatenkreuz_pos
  USING gist
  (pos);
