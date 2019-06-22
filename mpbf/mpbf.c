#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <math.h>
#include <string.h>
#include "bf.h"

#ifdef BARE_M
#include "mpconfig.h"
#include "misc.h"
#define realloc m_realloc
#define free m_free
#endif

#ifdef BARE_M
STATIC char __mpbf_returnval__[201] = "";
#else
STATIC char* __mpbf_returnval__;
#endif
STATIC int __mpbf_precdigits__;
STATIC int __mpbf_rnd_mode__;

STATIC mp_obj_t mpbf_init (void) {
	bf_initialize ();
    return mp_const_none;
}

STATIC mp_obj_t mpbf_set_params (mp_obj_t oprecdigits, mp_obj_t ornd_mode) {
	__mpbf_precdigits__ = mp_obj_get_int(oprecdigits);
	__mpbf_rnd_mode__ = mp_obj_get_int(ornd_mode);
	#ifndef BARE_M
	__mpbf_returnval__ = realloc(NULL, __mpbf_precdigits__+5); //reserve for digits+1 + '-', '.', 'e' and '\0'
	#endif
    return mp_const_none;
}

STATIC mp_obj_t mpbf_sop (mp_obj_t oa, mp_obj_t ob, mp_obj_t oop) {
	const char *a = mp_obj_str_get_str(oa);
	const char *b = mp_obj_str_get_str(ob);
	int op = mp_obj_get_int(oop);
	strcpy(__mpbf_returnval__, bf_sop (a, b, (bf_op_type_t) op, __mpbf_precdigits__, __mpbf_rnd_mode__));
	#ifdef BARE_M
	bf_initialize ();
	#endif
	return mp_obj_new_str(__mpbf_returnval__, strlen(__mpbf_returnval__));
}

STATIC mp_obj_t mpbf_finish (void) {
	#ifndef BARE_M
	free (__mpbf_returnval__);
	#endif
    bf_exit();	
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_0(mpbf_init_obj, mpbf_init);
STATIC MP_DEFINE_CONST_FUN_OBJ_2(mpbf_set_params_obj, mpbf_set_params);
STATIC MP_DEFINE_CONST_FUN_OBJ_3(mpbf_sop_obj, mpbf_sop);
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mpbf_finish_obj, mpbf_finish);

STATIC const mp_rom_map_elem_t mpbf_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_mpbf) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&mpbf_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_set_params), MP_ROM_PTR(&mpbf_set_params_obj) },
    { MP_ROM_QSTR(MP_QSTR_sop), MP_ROM_PTR(&mpbf_sop_obj) },
    { MP_ROM_QSTR(MP_QSTR_finish), MP_ROM_PTR(&mpbf_finish_obj) }
};

STATIC MP_DEFINE_CONST_DICT(mpbf_module_globals, mpbf_module_globals_table);

const mp_obj_module_t mpbf_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mpbf_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_mpbf, mpbf_user_cmodule, MODULE_MPBF_ENABLED);


