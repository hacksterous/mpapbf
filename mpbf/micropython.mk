MPBF_MOD_DIR := $(USERMOD_DIR)

SRC_USERMOD += $(MPBF_MOD_DIR)/mpbf.c
SRC_USERMOD += $(MPBF_MOD_DIR)/bf.c
SRC_USERMOD += $(MPBF_MOD_DIR)/libbf.c
SRC_USERMOD += $(MPBF_MOD_DIR)/cutils.c

CFLAGS_USERMOD += -I.
