
import wx
import OpenIPMI
import _entity
import _mc
import _saveprefs

class InvalidDomainInfo(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class DomainRefreshData:
    def __init__(self, d):
        self.d = d;

    def domain_cb(self, domain):
        self.d.ipmb_rescan_time = domain.get_ipmb_rescan_time()
        self.d.sel_rescan_time = domain.get_sel_rescan_time()
        self.d.ui.set_item_text(self.d.irscn,
                                "IPMB Rescan Time",
                                str(self.d.ipmb_rescan_time))
        self.d.ui.set_item_text(self.d.srscn, "SEL Rescan Time",
                                str(self.d.sel_rescan_time))
        self.d.ui.set_item_text(self.d.dguid, "GUID",
                                domain.get_guid())
        self.d.ui.set_item_text(self.d.dtype, "Type",
                                domain.get_type())


class DomainSelSet:
    def __init__(self, d):
        self.d = d;

    def HandleMenu(self, event):
        eitem = event.GetItem();
        menu = wx.Menu();
        item = menu.Append(-1, "Modify Value")
        self.d.ui.Bind(wx.EVT_MENU, self.modval, item)
        self.d.ui.PopupMenu(menu, self.d.ui.get_item_pos(eitem))
        menu.Destroy()

    def modval(self, event):
        dialog = wx.Dialog(None, -1, "Set SEL Rescan Time")
        self.dialog = dialog
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(dialog, -1, "Value:")
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.field = wx.TextCtrl(dialog, -1, str(self.d.sel_rescan_time))
        box.Add(self.field, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(box, 0, wx.ALIGN_CENTRE | wx.ALL, 2)
        
        bbox = wx.BoxSizer(wx.HORIZONTAL)
        cancel = wx.Button(dialog, -1, "Cancel")
        dialog.Bind(wx.EVT_BUTTON, self.cancel, cancel);
        bbox.Add(cancel, 0, wx.ALIGN_LEFT | wx.ALL, 5);
        ok = wx.Button(dialog, -1, "Ok")
        dialog.Bind(wx.EVT_BUTTON, self.ok, ok);
        bbox.Add(ok, 0, wx.ALIGN_LEFT | wx.ALL, 5);
        sizer.Add(bbox, 0, wx.ALIGN_CENTRE | wx.ALL, 2)

        dialog.SetSizer(sizer)
        dialog.Bind(wx.EVT_CLOSE, self.OnClose)
        dialog.CenterOnScreen();
        dialog.Show(True);

    def cancel(self, event):
        self.dialog.Close()

    def ok(self, event):
        val = self.field.GetValue()
        try:
            self.ival = int(val)
        except:
            return
        self.d.domain_id.convert_to_domain(self)
        self.dialog.Close()

    def OnClose(self, event):
        self.dialog.Destroy()

    def domain_cb(self, domain):
        domain.set_sel_rescan_time(self.ival)
        if (self.d.srscn != None):
            self.d.ui.set_item_text(self.d.srscn, "SEL Rescan Time",
                                    str(domain.get_sel_rescan_time()))
        
class DomainIPMBSet:
    def __init__(self, d):
        self.d = d;

    def HandleMenu(self, event):
        eitem = event.GetItem();
        menu = wx.Menu();
        item = menu.Append(-1, "Modify Value")
        self.d.ui.Bind(wx.EVT_MENU, self.modval, item)
        self.d.ui.PopupMenu(menu, self.d.ui.get_item_pos(eitem))
        menu.Destroy()

    def modval(self, event):
        dialog = wx.Dialog(None, -1, "Set IPMB Rescan Time")
        self.dialog = dialog
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(dialog, -1, "Value:")
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.field = wx.TextCtrl(dialog, -1, str(self.d.ipmb_rescan_time))
        box.Add(self.field, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(box, 0, wx.ALIGN_CENTRE | wx.ALL, 2)
        
        bbox = wx.BoxSizer(wx.HORIZONTAL)
        cancel = wx.Button(dialog, -1, "Cancel")
        dialog.Bind(wx.EVT_BUTTON, self.cancel, cancel);
        bbox.Add(cancel, 0, wx.ALIGN_LEFT | wx.ALL, 5);
        ok = wx.Button(dialog, -1, "Ok")
        dialog.Bind(wx.EVT_BUTTON, self.ok, ok);
        bbox.Add(ok, 0, wx.ALIGN_LEFT | wx.ALL, 5);
        sizer.Add(bbox, 0, wx.ALIGN_CENTRE | wx.ALL, 2)

        dialog.SetSizer(sizer)
        dialog.Bind(wx.EVT_CLOSE, self.OnClose)
        dialog.CenterOnScreen();
        dialog.Show(True);

    def cancel(self, event):
        self.dialog.Close()

    def ok(self, event):
        val = self.field.GetValue()
        try:
            self.ival = int(val)
        except:
            return
        self.d.domain_id.convert_to_domain(self)
        self.dialog.Close()

    def OnClose(self, event):
        self.dialog.Destroy()

    def domain_cb(self, domain):
        domain.set_ipmb_rescan_time(self.ival)
        if (self.d.srscn != None):
            self.d.ui.set_item_text(self.d.irscn, "IPMB Rescan Time",
                                    str(domain.get_ipmb_rescan_time()))
        

class Domain:
    def __init__(self, mainhandler, name):
        if (mainhandler.domains.has_key(name)):
            raise InvalidDomainInfo("Domain name already exists")
        self.name = name
        self.mainhandler = mainhandler
        self.ui = mainhandler.ui
        self.entities = { }
        self.mcs = { }

        # connection attributes
        self.contype = ""
        self.address = ""
        self.port = ""
        self.username = ""
        self.password = ""
        self.privilege = ""
        self.authtype = ""
        self.auth_alg = ""
        self.integ_alg = ""
        self.conf_alg = ""
        self.bmc_key = ""
        self.address2 = ""
        self.port2 = ""
        self.hacks = [ ]
        self.lookup_uses_priv = False

        self.updater = DomainRefreshData(self)
        self.domain_id = None
        mainhandler.domains[name] = self
        
        self.ui.add_domain(self)
        self.ipmb_rescan_time = 0
        self.sel_rescan_time = 0
        self.irscn = self.ui.prepend_item(self, "IPMB Rescan Time", None,
                                          DomainIPMBSet(self))
        self.srscn = self.ui.prepend_item(self, "SEL Rescan Time", None,
                                          DomainSelSet(self))
        self.dguid = self.ui.prepend_item(self, "GUID", None)
        self.dtype = self.ui.prepend_item(self, "Type", None)

    def __str__(self):
        return self.name

    def getTag(self):
        return "domain";

    def getAttr(self):
        if (self.contype == ""):
            return
        attrl = [ ("name", self.name), ("contype", self.contype) ]
        if (self.address != ""):
            attrl.append(("address", self.address))
        if (self.address != ""):
            attrl.append(("port", self.port))
        if (self.address != ""):
            attrl.append(("username", self.username))
        if (self.address != ""):
            attrl.append(("password", self.password))
        if (self.privilege != ""):
            attrl.append(("privilege", self.privilege))
        if (self.authtype != ""):
            attrl.append(("authtype", self.authtype))
        if (self.auth_alg != ""):
            attrl.append(("auth_alg", self.auth_alg))
        if (self.integ_alg != ""):
            attrl.append(("integ_alg", self.integ_alg))
        if (self.conf_alg != ""):
            attrl.append(("conf_alg", self.conf_alg))
        if (self.bmc_key != ""):
            attrl.append(("bmc_key", self.bmc_key))
        if (self.address2 != ""):
            attrl.append(("address2", self.address2))
            if (self.port2 != ""):
                attrl.append(("port2", self.port2))
        hlen = len(self.hacks)
        if (hlen > 0):
            hvals = self.hacks[0]
            for i in range(1, hlen):
                hvals = hvals + ' ' + self.hacks[i]
            attrl.append(("hacks", hvals))
        return attrl

    def DoUpdate(self):
        if (self.domain_id != None):
            self.domain_id.convert_to_domain(self.updater)

    def HandleExpand(self, event):
        self.DoUpdate()

    def SetType(self, contype):
        self.contype = contype

    def SetAddress(self, addr):
        self.address = addr

    def SetPort(self, port):
        self.port = port

    def SetUsername(self, username):
        self.username = username

    def SetPassword(self, password):
        self.password = password

    def SetPrivilege(self, value):
        if (value == 'default'):
            value = ''
        self.privilege = value
        
    def SetAuthtype(self, value):
        if (value == 'default'):
            value = ''
        self.authtype = value
        
    def SetAuth_alg(self, value):
        if (value == 'default'):
            value = ''
        self.auth_alg = value
        
    def SetInteg_alg(self, value):
        if (value == 'default'):
            value = ''
        self.integ_alg = value
        
    def SetConf_alg(self, value):
        if (value == 'default'):
            value = ''
        self.conf_alg = value
        
    def SetBmc_key(self, value):
        self.bmc_key = value
        
    def SetAddress2(self, value):
        self.address2 = value
        
    def SetPort2(self, value):
        self.port2 = value
        
    def AddHack(self, value):
        self.hacks.append(value)
        
    def AddHacks(self, values):
        self.hacks.extend(values.split())
        
    def Lookup_uses_priv(self, value):
        self.lookup_uses_priv = value

    def Connect(self):
        if (self.contype == "smi"):
            if (self.port == ""):
                raise InvalidDomainInfo("No port specified")
            self.domain_id = OpenIPMI.open_domain2(self.name,
                                                   ["smi", self.port])
        elif (self.contype == "lan"):
            if (self.address == ""):
                raise InvalidDomainInfo("No address specified")
            attr = [ "lan" ]
            if (self.port != ""):
                attr.extend(["-p", self.port])
            if (self.username != ""):
                attr.extend(["-U", self.username])
            if (self.password != ""):
                attr.extend(["-P", self.password])
            if (self.authtype != ""):
                attr.extend(["-A", self.authtype])
            if (self.privilege != ""):
                attr.extend(["-L", self.privilege])
            if (self.auth_alg != ""):
                attr.extend(["-Ra", self.auth_alg])
            if (self.integ_alg != ""):
                attr.extend(["-Ri", self.integ_alg])
            if (self.conf_alg != ""):
                attr.extend(["-Rc", self.conf_alg])
            if (self.bmc_key != ""):
                attr.extend(["-Rk", self.bmc_key])
            if (self.lookup_uses_priv):
                attr.append("-Rl")
            for h in self.hacks:
                attr.extend(["-H", h])
            if (self.address2 != ""):
                attr.append("-s")
                if (self.port2 != ""):
                    attr.extend(["-p2", self.port2])
            attr.append(self.address)
            if (self.address2 != ""):
                attr.append(self.address2)
            self.domain_id = OpenIPMI.open_domain2(self.name, attr)
            if (self.domain_id == None):
                raise InvalidDomainInfo("Open domain failed, invalid parms")
        else:
            raise InvalidDomainInfo("Invalid connection type: " + self.contype)

    def connected(self, domain):
        domain.add_entity_update_handler(self)
        domain.add_mc_update_handler(self)
        DomainRefreshData(self)

    def entity_update_cb(self, op, domain, entity):
        if (op == "added"):
            e = _entity.Entity(self, entity)
            entity.add_sensor_update_handler(e)
            entity.add_control_update_handler(e)
        elif (op == "removed"):
            self.entities[entity.get_name()].remove()
        
    def mc_update_cb(self, op, domain, mc):
        if (op == "added"):
            _mc.MC(self, mc)
        elif (op == "removed"):
            self.entities[mc.get_name()].remove()
        
    def domain_cb(self, domain):
        domain.close(self)

    def domain_close_done_cb(self):
        pass
        
    def remove(self):
        if (self.domain_id != None):
            self.domain_id.convert_to_domain(self)
        self.mainhandler.domains.pop(self.name);
        self.ui.remove_domain(self)
        
class _DomainRestore(_saveprefs.RestoreHandler):
    def __init__(self):
        _saveprefs.RestoreHandler.__init__(self, "domain")

    def restore(self, mainhandler, attrhash):
        if "name" not in attrhash:
            return
        if "contype" not in attrhash:
            return
        name = str(attrhash["name"])
        del attrhash["name"]
        contype = str(attrhash["contype"])
        del attrhash["contype"]
        d = Domain(mainhandler, name);
        d.SetType(contype)
        
        for attr in attrhash.items():
            attrn = str(attr[0])
            value = str(attr[1])
            if (attrn == "password"):
                d.SetPassword(value)
            elif (attrn == "username"):
                d.SetUsername(value)
            elif (attrn == "address"):
                d.SetAddress(value)
            elif (attrn == "port"):
                d.SetPort(value)
            elif (attrn == "privilege"):
                d.SetPrivilege(value)
            elif (attrn == "authtype"):
                d.SetAuthtype(value)
            elif (attrn == "auth_alg"):
                d.SetAuth_alg(value)
            elif (attrn == "integ_alg"):
                d.SetInteg_alg(value)
            elif (attrn == "conf_alg"):
                d.SetConf_alg(value)
            elif (attrn == "bmc_key"):
                d.SetBmc_key(value)
            elif (attrn == "address2"):
                d.SetAddress2(value)
            elif (attrn == "port2"):
                d.SetPort2(value)
            elif (attrn == "hacks"):
                d.AddHacks(value)
            elif (attrn == "lookup_uses_priv"):
                d.Lookup_uses_priv(True)

        d.Connect()

_DomainRestore()