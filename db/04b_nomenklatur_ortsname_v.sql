-- View: av_basisplan.nomenklatur_ortsname_v

-- DROP VIEW av_basisplan.nomenklatur_ortsname_v;

CREATE OR REPLACE VIEW av_basisplan.nomenklatur_ortsname_v AS 
 SELECT pos.ogc_fid, pos.tid, pos.ortsnamepos_von, pos.pos, 
        CASE
            WHEN pos.ori IS NULL THEN 100::double precision
            ELSE pos.ori
        END AS ori, pos.hali_txt, pos.vali_txt, pos.groesse_txt, pos.stil_txt, pos.gem_bfs, pos.los, pos.lieferdatum, oname.name, st_x(pos.pos) AS xlabel, st_y(pos.pos) AS ylabel
   FROM av_avdpool_ch.nomenklatur_ortsnamepos pos, av_avdpool_ch.nomenklatur_ortsname oname
  WHERE oname.tid::text = pos.ortsnamepos_von::text;

ALTER TABLE av_basisplan.nomenklatur_ortsname_v OWNER TO stefan;
GRANT ALL ON TABLE av_basisplan.nomenklatur_ortsname_v TO stefan;
GRANT SELECT ON TABLE av_basisplan.nomenklatur_ortsname_v TO mspublic;

