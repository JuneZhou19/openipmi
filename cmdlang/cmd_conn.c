/*
 * cmd_conn.c
 *
 * A command interpreter for OpenIPMI
 *
 * Author: MontaVista Software, Inc.
 *         Corey Minyard <minyard@mvista.com>
 *         source@mvista.com
 *
 * Copyright 2004 MontaVista Software Inc.
 *
 *  This program is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Lesser General Public License
 *  as published by the Free Software Foundation; either version 2 of
 *  the License, or (at your option) any later version.
 *
 *
 *  THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED
 *  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 *  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 *  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
 *  OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 *  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
 *  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
 *  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *  You should have received a copy of the GNU Lesser General Public
 *  License along with this program; if not, write to the Free
 *  Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

#include <errno.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>
#include <stdio.h>
#include <OpenIPMI/ipmiif.h>
#include <OpenIPMI/ipmi_domain.h>
#include <OpenIPMI/ipmi_event.h>
#include <OpenIPMI/ipmi_mc.h>
#include <OpenIPMI/ipmi_cmdlang.h>
#include <OpenIPMI/ipmi_int.h>
#include <OpenIPMI/ipmi_conn.h>

static void
con_list_handler(ipmi_domain_t *domain, int conn, void *cb_data)
{
    ipmi_cmd_info_t *cmd_info = cb_data;
    ipmi_cmdlang_t  *cmdlang = ipmi_cmdinfo_get_cmdlang(cmd_info);
    char            conn_name[IPMI_MAX_DOMAIN_NAME_LEN+20];
    int             p;

    if (cmdlang->err)
	return;

    p = ipmi_domain_get_name(domain, conn_name, sizeof(conn_name));
    snprintf(conn_name+p, sizeof(conn_name)-p, ".%d", conn);
    ipmi_cmdlang_out(cmd_info, "Name", conn_name);
}

static void
con_list(ipmi_domain_t *domain, void *cb_data)
{
    ipmi_domain_iterate_connections(domain, con_list_handler, cb_data);
}

static void
con_info(ipmi_domain_t *domain, int conn, void *cb_data)
{
    ipmi_cmd_info_t *cmd_info = cb_data;
    char            conn_name[IPMI_MAX_DOMAIN_NAME_LEN+20];
    int             p;
    int             rv;
    unsigned int    act;

    rv = ipmi_domain_is_connection_active(domain, conn, &act);
    if (rv)
	return;

    p = ipmi_domain_get_name(domain, conn_name, sizeof(conn_name));
    snprintf(conn_name+p, sizeof(conn_name)-p, ".%d", conn);

    ipmi_cmdlang_out(cmd_info, "Connection", NULL);
    ipmi_cmdlang_down(cmd_info);
    ipmi_cmdlang_out(cmd_info, "Name", conn_name);
    ipmi_cmdlang_out_bool(cmd_info, "Active", act);
    ipmi_cmdlang_up(cmd_info);
}

static void
con_activate(ipmi_domain_t *domain, int conn, void *cb_data)
{
    ipmi_cmd_info_t *cmd_info = cb_data;
    ipmi_cmdlang_t *cmdlang = ipmi_cmdinfo_get_cmdlang(cmd_info);
    int             rv;

printf("**a");
    rv = ipmi_domain_activate_connection(domain, conn);
    if (rv) {
	cmdlang->errstr = "Unable to activate connection";
	cmdlang->err = rv;
	ipmi_domain_get_name(domain, cmdlang->objstr,
			     cmdlang->objstr_len);
	cmdlang->location = "cmd_conn.c(con_activate)";
    }
}

static ipmi_cmdlang_cmd_t *conn_cmds;

static ipmi_cmdlang_init_t cmds_conn[] =
{
    { "con", NULL,
      "- Commands dealing with connections",
      NULL, NULL, &conn_cmds},
    { "list", &conn_cmds,
      "<domain> - List all the connection in the domain",
      ipmi_cmdlang_domain_handler, con_list,  NULL },
    { "info", &conn_cmds,
      "<connection> - Dump information about a connection",
      ipmi_cmdlang_connection_handler, con_info, NULL },
    { "activate", &conn_cmds,
      "<connection> - Dump information about a connection",
      ipmi_cmdlang_connection_handler, con_activate, NULL },
};
#define CMDS_CONN_LEN (sizeof(cmds_conn)/sizeof(ipmi_cmdlang_init_t))

int
ipmi_cmdlang_con_init(void)
{
    return ipmi_cmdlang_reg_table(cmds_conn, CMDS_CONN_LEN);
}
