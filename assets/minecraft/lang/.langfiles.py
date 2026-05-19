import os
import shutil
import sys

locales = [
    "af_za","ar_sa","ast_es","az_az","ba_ru","bar","be_by","bg_bg","br_fr","bs_ba","ca_es","cs_cz","cy_gb","da_dk","de_de","el_gr","en_gb","en_us","es_es","es_mx","et_ee","eu_es","fa_ir","fi_fi","fr_fr","ga_ie","gd_gb","gl_es","he_il","hi_in","hr_hr","hu_hu","hy_am","id_id","is_is","it_it","ja_jp","ka_ge","kk_kz","ko_kr","la_la","lb_lu","lt_lt","lv_lv","mk_mk","mn_mn","ms_my","mt_mt","nl_nl","no_no","pl_pl","pt_br","pt_pt","ro_ro","ru_ru","sk_sk","sl_si","sq_al","sr_cs","sv_se","th_th","tr_tr","uk_ua","vi_vn","zh_cn","zh_tw"
]

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
source_file = os.path.join(script_dir, ".template.json")

if not os.path.exists(source_file):
    sys.exit(1)

for locale in locales:
    target_file = os.path.join(script_dir, f"{locale}.json")
    shutil.copyfile(source_file, target_file)
    print(f"Generated: {locale}.json")
