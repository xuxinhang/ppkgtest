"""
   Copyright 2013, Shinya Takamaeda-Yamazaki and Contributors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from pison import Parser
from astnode import *


__ = 0

class VerilogParser(Parser):
    'Verilog HDL Parser'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = '__FILE__'
        self.directives = []
        self.default_nettype = 'wire'

    def get_directives(self):
        return tuple(self.directives)

    def get_default_nettype(self):
        return self.default_nettype

    grammar_engine = 'lalr'

    # Expression Precedence
    # Reference: http://hp.vector.co.jp/authors/VA016670/verilog/index.html
    precedence = [
        # <- Weak
        ('left', 'LOR'),
        ('left', 'LAND'),
        ('left', 'OR'),
        ('left', 'XOR', 'XNOR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NE', 'EQL', 'NEL'),
        ('left', 'LT', 'GT', 'LE', 'GE'),
        ('left', 'LSHIFT', 'RSHIFT', 'LSHIFTA', 'RSHIFTA'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD'),
        ('left', 'POWER'),
        ('right', 'UMINUS', 'UPLUS', 'ULNOT', 'UNOT',
         'UAND', 'UNAND', 'UOR', 'UNOR', 'UXOR', 'UXNOR'),
        # -> Strong
    ]

    # --------------------------------------------------------------------------
    # Parse Rule Definition
    # --------------------------------------------------------------------------
    @__('source_text', 'description')
    def p_source_text(self, p):
        p[0] = Source(name='', description=p[1], lineno=1)

    @__('description', 'definitions')
    def p_description(self, p):
        p[0] = Description(definitions=p[1], lineno=1)

    @__('definitions', 'definitions', 'definition')
    def p_definitions(self, p):
        p[0] = p[1] + (p[2],)

    @__('definitions', 'definition')
    def p_definitions_one(self, p):
        p[0] = (p[1],)

    @__('definition', 'moduledef')
    def p_definition(self, p):
        p[0] = p[1]

    @__('definition', 'pragma')
    def p_definition_pragma(self, p):
        p[0] = p[1]

    # --------------------------------------------------------------------------
    @__('pragma', 'LPAREN', 'TIMES', 'ID', 'EQUALS', 'expression', 'TIMES', 'RPAREN')
    def p_pragma_assign(self, p):
        p[0] = Pragma(PragmaEntry(p[3], p[5], lineno=1), lineno=1)

    @__('pragma', 'LPAREN', 'TIMES', 'ID', 'TIMES', 'RPAREN')
    def p_pragma(self, p):
        p[0] = Pragma(PragmaEntry(p[3], lineno=1), lineno=1)

    # --------------------------------------------------------------------------
    @__('moduledef', 'MODULE', 'modulename', 'paramlist', 'portlist', 'items', 'ENDMODULE')
    def p_moduledef(self, p):
        p[0] = ModuleDef(name=p[2], paramlist=p[3], portlist=p[4], items=p[5],
                         default_nettype=self.get_default_nettype(), lineno=1)
        p[0].end_lineno = 6

    @__('modulename', 'ID')
    def p_modulename(self, p):
        p[0] = p[1]

    @__('modulename', 'SENS_OR')
    def p_modulename_or(self, p):
        p[0] = p[1]

    @__('paramlist', 'DELAY', 'LPAREN', 'params', 'RPAREN')
    def p_paramlist(self, p):
        p[0] = Paramlist(params=p[3], lineno=1)

    @__('paramlist', 'empty')
    def p_paramlist_empty(self, p):
        p[0] = Paramlist(params=())

    @__('params', 'params_begin', 'param_end')
    def p_params(self, p):
        p[0] = p[1] + (p[2],)

    @__('params_begin', 'params_begin', 'param')
    def p_params_begin(self, p):
        p[0] = p[1] + (p[2],)

    @__('params_begin', 'param')
    def p_params_begin_one(self, p):
        p[0] = (p[1],)

    @__('params', 'param_end')
    def p_params_one(self, p):
        p[0] = (p[1],)

    @__('param', 'PARAMETER', 'param_substitution_list', 'COMMA')
    def p_param(self, p):
        paramlist = [Parameter(rname, rvalue, lineno=2)
                     for rname, rvalue in p[2]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('param', 'PARAMETER', 'SIGNED', 'param_substitution_list', 'COMMA')
    def p_param_signed(self, p):
        paramlist = [Parameter(rname, rvalue, signed=True, lineno=2)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('param', 'PARAMETER', 'width', 'param_substitution_list', 'COMMA')
    def p_param_width(self, p):
        paramlist = [Parameter(rname, rvalue, p[2], lineno=3)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('param', 'PARAMETER', 'SIGNED', 'width', 'param_substitution_list', 'COMMA')
    def p_param_signed_width(self, p):
        paramlist = [Parameter(rname, rvalue, p[3], signed=True, lineno=3)
                     for rname, rvalue in p[4]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('param', 'PARAMETER', 'INTEGER', 'param_substitution_list', 'COMMA')
    def p_param_integer(self, p):
        paramlist = [Parameter(rname, rvalue, lineno=3)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('param_end', 'PARAMETER', 'param_substitution_list')
    def p_param_end(self, p):
        paramlist = [Parameter(rname, rvalue, lineno=2)
                     for rname, rvalue in p[2]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('param_end', 'PARAMETER', 'SIGNED', 'param_substitution_list')
    def p_param_end_signed(self, p):
        paramlist = [Parameter(rname, rvalue, signed=True, lineno=2)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('param_end', 'PARAMETER', 'width', 'param_substitution_list')
    def p_param_end_width(self, p):
        paramlist = [Parameter(rname, rvalue, p[2], lineno=3)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('param_end', 'PARAMETER', 'SIGNED', 'width', 'param_substitution_list')
    def p_param_end_signed_width(self, p):
        paramlist = [Parameter(rname, rvalue, p[3], signed=True, lineno=3)
                     for rname, rvalue in p[4]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('param_end', 'PARAMETER', 'INTEGER', 'param_substitution_list')
    def p_param_end_integer(self, p):
        paramlist = [Parameter(rname, rvalue, lineno=3)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('portlist', 'LPAREN', 'ports', 'RPAREN', 'SEMICOLON')
    def p_portlist(self, p):
        p[0] = Portlist(ports=p[2], lineno=1)

    @__('portlist', 'LPAREN', 'ioports', 'RPAREN', 'SEMICOLON')
    def p_portlist_io(self, p):
        p[0] = Portlist(ports=p[2], lineno=1)

    @__('portlist', 'LPAREN', 'RPAREN', 'SEMICOLON')
    def p_portlist_paren_empty(self, p):
        p[0] = Portlist(ports=(), lineno=1)

    @__('portlist', 'SEMICOLON')
    def p_portlist_empty(self, p):
        p[0] = Portlist(ports=(), lineno=1)

    @__('ports', 'ports', 'COMMA', 'portname')
    def p_ports(self, p):
        port = Port(name=p[3], width=None, dimensions=None, type=None, lineno=1)
        p[0] = p[1] + (port,)

    @__('ports', 'portname')
    def p_ports_one(self, p):
        port = Port(name=p[1], width=None, dimensions=None, type=None, lineno=1)
        p[0] = (port,)

    @__('portname', 'ID')
    def p_portname(self, p):
        p[0] = p[1]

    @__('sigtypes', 'sigtypes', 'sigtype')
    def p_sigtypes(self, p):
        p[0] = p[1] + (p[2],)

    @__('sigtypes', 'sigtype')
    def p_sigtypes_one(self, p):
        p[0] = (p[1],)

    @__('sigtype', 'INPUT')
    def p_sigtype_input(self, p):
        p[0] = p[1]

    @__('sigtype', 'OUTPUT')
    def p_sigtype_output(self, p):
        p[0] = p[1]

    @__('sigtype', 'INOUT')
    def p_sigtype_inout(self, p):
        p[0] = p[1]

    @__('sigtype', 'TRI')
    def p_sigtype_tri(self, p):
        p[0] = p[1]

    @__('sigtype', 'REG')
    def p_sigtype_reg(self, p):
        p[0] = p[1]

    @__('sigtype', 'LOGIC')
    def p_sigtype_logic(self, p):
        p[0] = p[1]

    @__('sigtype', 'WIRE')
    def p_sigtype_wire(self, p):
        p[0] = p[1]

    @__('sigtype', 'SIGNED')
    def p_sigtype_signed(self, p):
        p[0] = p[1]

    @__('sigtype', 'SUPPLY0')
    def p_sigtype_supply0(self, p):
        p[0] = p[1]

    @__('sigtype', 'SUPPLY1')
    def p_sigtype_supply1(self, p):
        p[0] = p[1]

    @__('ioports', 'ioports', 'COMMA', 'ioport')
    def p_ioports(self, p):
        if isinstance(p[3], str):
            t = None
            for r in reversed(p[1]):
                if isinstance(r.first, Input):
                    t = Ioport(Input(name=p[3], width=r.first.width, lineno=3),
                               lineno=3)
                    break
                if isinstance(r.first, Output) and r.second is None:
                    t = Ioport(Output(name=p[3], width=r.first.width, lineno=3),
                               lineno=3)
                    break
                if isinstance(r.first, Output) and isinstance(r.second, Reg):
                    t = Ioport(Output(name=p[3], width=r.first.width, lineno=3),
                               Reg(name=p[3], width=r.first.width,
                                   lineno=3),
                               lineno=3)
                    break
                if isinstance(r.first, Inout):
                    t = Ioport(Inout(name=p[3], width=r.first.width, lineno=3),
                               lineno=3)
                    break
            p[0] = p[1] + (t,)
        else:
            p[0] = p[1] + (p[3],)

    @__('ioports', 'ioport_head')
    def p_ioports_one(self, p):
        p[0] = (p[1],)

    def create_ioport(self, sigtypes, name, width=None, dimensions=None, lineno=0):
        self.typecheck_ioport(sigtypes)
        first = None
        second = None
        signed = False
        if 'signed' in sigtypes:
            signed = True
        if 'input' in sigtypes:
            first = Input(name=name, width=width, signed=signed,
                          dimensions=dimensions, lineno=lineno)
        if 'output' in sigtypes:
            first = Output(name=name, width=width, signed=signed,
                           dimensions=dimensions, lineno=lineno)
        if 'inout' in sigtypes:
            first = Inout(name=name, width=width, signed=signed,
                          dimensions=dimensions, lineno=lineno)
        if 'wire' in sigtypes:
            second = Wire(name=name, width=width, signed=signed,
                          dimensions=dimensions, lineno=lineno)
        if 'reg' in sigtypes:
            second = Reg(name=name, width=width, signed=signed,
                         dimensions=dimensions, lineno=lineno)
        if 'tri' in sigtypes:
            second = Tri(name=name, width=width, signed=signed,
                         dimensions=dimensions, lineno=lineno)
        return Ioport(first, second, lineno=lineno)

    def typecheck_ioport(self, sigtypes):
        if 'input' not in sigtypes and 'output' not in sigtypes and 'inout' not in sigtypes:
            raise ParseError("Syntax Error")
        if 'input' in sigtypes and 'output' in sigtypes:
            raise ParseError("Syntax Error")
        if 'inout' in sigtypes and 'output' in sigtypes:
            raise ParseError("Syntax Error")
        if 'inout' in sigtypes and 'input' in sigtypes:
            raise ParseError("Syntax Error")
        if 'input' in sigtypes and 'reg' in sigtypes:
            raise ParseError("Syntax Error")
        if 'inout' in sigtypes and 'reg' in sigtypes:
            raise ParseError("Syntax Error")
        if 'input' in sigtypes and 'tri' in sigtypes:
            raise ParseError("Syntax Error")
        if 'output' in sigtypes and 'tri' in sigtypes:
            raise ParseError("Syntax Error")

    @__('ioport', 'sigtypes', 'portname')
    def p_ioport(self, p):
        p[0] = self.create_ioport(p[1], p[2], lineno=2)

    @__('ioport', 'sigtypes', 'width', 'portname')
    def p_ioport_width(self, p):
        p[0] = self.create_ioport(p[1], p[3], width=p[2], lineno=3)

    @__('ioport', 'sigtypes', 'width', 'portname', 'dimensions')
    def p_ioport_dimensions(self, p):
        p[0] = self.create_ioport(p[1], p[3], width=p[2], dimensions=p[4], lineno=3)

    @__('ioport_head', 'sigtypes', 'portname')
    def p_ioport_head(self, p):
        p[0] = self.create_ioport(p[1], p[2], lineno=2)

    @__('ioport_head', 'sigtypes', 'width', 'portname')
    def p_ioport_head_width(self, p):
        p[0] = self.create_ioport(p[1], p[3], width=p[2], lineno=3)

    @__('ioport_head', 'sigtypes', 'width', 'portname', 'dimensions')
    def p_ioport_head_dimensions(self, p):
        p[0] = self.create_ioport(p[1], p[3], width=p[2], dimensions=p[4], lineno=3)

    @__('ioport', 'portname')
    def p_ioport_portname(self, p):
        p[0] = p[1]

    @__('width', 'LBRACKET', 'expression', 'COLON', 'expression', 'RBRACKET')
    def p_width(self, p):
        p[0] = Width(p[2], p[4], lineno=1)

    @__('length', 'LBRACKET', 'expression', 'COLON', 'expression', 'RBRACKET')
    def p_length(self, p):
        p[0] = Length(p[2], p[4], lineno=1)

    @__('dimensions', 'dimensions', 'length')
    def p_dimensions(self, p):
        dims = p[1].lengths + [p[2]]
        p[0] = Dimensions(dims, lineno=1)

    @__('dimensions', 'length')
    def p_dimensions_one(self, p):
        dims = [p[1]]
        p[0] = Dimensions(dims, lineno=1)

    @__('items', 'items', 'item')
    def p_items(self, p):
        p[0] = p[1] + (p[2],)

    @__('items', 'item')
    def p_items_one(self, p):
        p[0] = (p[1],)

    @__('items', 'empty')
    def p_items_empty(self, p):
        p[0] = ()

    @__('item', ['standard_item', 'generate'])
    def p_item(self, p):
        p[0] = p[1]

    @__('standard_item', [
        'decl',
        'integerdecl',
        'realdecl',
        'declassign',
        'parameterdecl',
        'localparamdecl',
        'genvardecl',
        'assignment',
        'always',
        'always_ff',
        'always_comb',
        'always_latch',
        'initial',
        'instance',
        'function',
        'task',
        'pragma',
    ])
    def p_standard_item(self, p):
        p[0] = p[1]

    # Signal Decl
    def create_decl(self, sigtypes, name, width=None, dimensions=None, lineno=0):
        self.typecheck_decl(sigtypes, dimensions)
        decls = []
        signed = False
        if 'signed' in sigtypes:
            signed = True
        if 'input' in sigtypes:
            decls.append(Input(name=name, width=width,
                               signed=signed, lineno=lineno, dimensions=dimensions))
        if 'output' in sigtypes:
            decls.append(Output(name=name, width=width,
                                signed=signed, lineno=lineno, dimensions=dimensions))
        if 'inout' in sigtypes:
            decls.append(Inout(name=name, width=width,
                               signed=signed, lineno=lineno, dimensions=dimensions))
        if 'wire' in sigtypes:
            decls.append(Wire(name=name, width=width,
                              signed=signed, lineno=lineno, dimensions=dimensions))
        if 'reg' in sigtypes:
            decls.append(Reg(name=name, width=width,
                             signed=signed, lineno=lineno, dimensions=dimensions))
        if 'tri' in sigtypes:
            decls.append(Tri(name=name, width=width,
                             signed=signed, lineno=lineno, dimensions=dimensions))
        if 'supply0' in sigtypes:
            decls.append(Supply(name=name, value=IntConst('0', lineno=lineno),
                                width=width, signed=signed, lineno=lineno))
        if 'supply1' in sigtypes:
            decls.append(Supply(name=name, value=IntConst('1', lineno=lineno),
                                width=width, signed=signed, lineno=lineno))
        return decls

    def typecheck_decl(self, sigtypes, dimensions=None):
        if ('supply0' in sigtypes or 'supply1' in sigtypes) and \
           dimensions is not None:
            raise ParseError("SyntaxError")
        if len(sigtypes) == 1 and 'signed' in sigtypes:
            raise ParseError("Syntax Error")
        if 'input' in sigtypes and 'output' in sigtypes:
            raise ParseError("Syntax Error")
        if 'inout' in sigtypes and 'output' in sigtypes:
            raise ParseError("Syntax Error")
        if 'inout' in sigtypes and 'input' in sigtypes:
            raise ParseError("Syntax Error")
        if 'input' in sigtypes and 'reg' in sigtypes:
            raise ParseError("Syntax Error")
        if 'inout' in sigtypes and 'reg' in sigtypes:
            raise ParseError("Syntax Error")
        if 'input' in sigtypes and 'tri' in sigtypes:
            raise ParseError("Syntax Error")
        if 'output' in sigtypes and 'tri' in sigtypes:
            raise ParseError("Syntax Error")

    @__('decl', 'sigtypes', 'declnamelist', 'SEMICOLON')
    def p_decl(self, p):
        decllist = []
        for rname, rdimensions in p[2]:
            decllist.extend(self.create_decl(p[1], rname, dimensions=rdimensions,
                                             lineno=2))
        p[0] = Decl(tuple(decllist), lineno=1)

    @__('decl', 'sigtypes', 'width', 'declnamelist', 'SEMICOLON')
    def p_decl_width(self, p):
        decllist = []
        for rname, rdimensions in p[3]:
            decllist.extend(self.create_decl(p[1], rname, width=p[2], dimensions=rdimensions,
                                             lineno=3))
        p[0] = Decl(tuple(decllist), lineno=1)

    @__('declnamelist', 'declnamelist', 'COMMA', 'declname')
    def p_declnamelist(self, p):
        p[0] = p[1] + (p[3],)

    @__('declnamelist', 'declname')
    def p_declnamelist_one(self, p):
        p[0] = (p[1],)

    @__('declname', 'ID')
    def p_declname(self, p):
        p[0] = (p[1], None)

    @__('declname', 'ID', 'dimensions')
    def p_declarray(self, p):
        p[0] = (p[1], p[2])

    # Decl and Assign
    def create_declassign(self, sigtypes, name, assign, width=None, lineno=0):
        self.typecheck_declassign(sigtypes)
        decls = []
        signed = False
        if 'signed' in sigtypes:
            signed = True
        if 'input' in sigtypes:
            decls.append(Input(name=name, width=width,
                               signed=signed, lineno=lineno))
        if 'output' in sigtypes:
            decls.append(Output(name=name, width=width,
                                signed=signed, lineno=lineno))
        if 'inout' in sigtypes:
            decls.append(Inout(name=name, width=width,
                               signed=signed, lineno=lineno))
        if 'wire' in sigtypes:
            decls.append(Wire(name=name, width=width,
                              signed=signed, lineno=lineno))
        if 'reg' in sigtypes:
            decls.append(Reg(name=name, width=width,
                             signed=signed, lineno=lineno))
        decls.append(assign)
        return decls

    def typecheck_declassign(self, sigtypes):
        if len(sigtypes) == 1 and 'signed' in sigtypes:
            raise ParseError("Syntax Error")
        if 'reg' not in sigtypes and 'wire' not in sigtypes:
            raise ParseError("Syntax Error")
        if 'input' in sigtypes and 'output' in sigtypes:
            raise ParseError("Syntax Error")
        if 'inout' in sigtypes and 'output' in sigtypes:
            raise ParseError("Syntax Error")
        if 'inout' in sigtypes and 'input' in sigtypes:
            raise ParseError("Syntax Error")
        if 'input' in sigtypes and 'reg' in sigtypes:
            raise ParseError("Syntax Error")
        if 'inout' in sigtypes and 'reg' in sigtypes:
            raise ParseError("Syntax Error")
        if 'supply0' in sigtypes and len(sigtypes) != 1:
            raise ParseError("Syntax Error")
        if 'supply1' in sigtypes and len(sigtypes) != 1:
            raise ParseError("Syntax Error")

    @__('declassign', 'sigtypes', 'declassign_element', 'SEMICOLON')
    def p_declassign(self, p):
        decllist = self.create_declassign(
            p[1], p[2][0], p[2][1], lineno=2)
        p[0] = Decl(decllist, lineno=1)

    @__('declassign', 'sigtypes', 'width', 'declassign_element', 'SEMICOLON')
    def p_declassign_width(self, p):
        decllist = self.create_declassign(
            p[1], p[3][0], p[3][1], width=p[2], lineno=3)
        p[0] = Decl(tuple(decllist), lineno=1)

    @__('declassign_element', 'ID', 'EQUALS', 'rvalue')
    def p_declassign_element(self, p):
        assign = Assign(Lvalue(Identifier(p[1], lineno=1), lineno=1),
                        p[3], lineno=1)
        p[0] = (p[1], assign)

    @__('declassign_element', 'delays', 'ID', 'EQUALS', 'delays', 'rvalue')
    def p_declassign_element_delay(self, p):
        assign = Assign(Lvalue(Identifier(p[2], lineno=1), lineno=2),
                        p[5], p[1], p[4], lineno=2)
        p[0] = (p[1], assign)

    # Integer
    @__('integerdecl', 'INTEGER', 'integernamelist', 'SEMICOLON')
    def p_integerdecl(self, p):
        intlist = [Integer(rname,
                           Width(msb=IntConst('31', lineno=2),
                                 lsb=IntConst('0', lineno=2),
                                 lineno=2),
                           signed=True,
                           value=rvalue,
                           lineno=2) for rname, rvalue in p[2]]
        p[0] = Decl(tuple(intlist), lineno=1)

    @__('integerdecl', 'INTEGER', 'SIGNED', 'integernamelist', 'SEMICOLON')
    def p_integerdecl_signed(self, p):
        intlist = [Integer(rname,
                           Width(msb=IntConst('31', lineno=3),
                                 lsb=IntConst('0', lineno=3),
                                 lineno=3),
                           signed=True,
                           value=rvalue,
                           lineno=3) for rname, rvalue in p[2]]
        p[0] = Decl(tuple(intlist), lineno=1)

    @__('integernamelist', 'integernamelist', 'COMMA', 'integername')
    def p_integernamelist(self, p):
        p[0] = p[1] + (p[3],)

    @__('integernamelist', 'integername')
    def p_integernamelist_one(self, p):
        p[0] = (p[1],)

    @__('integername', 'ID', 'EQUALS', 'rvalue')
    def p_integername_init(self, p):
        p[0] = (p[1], p[3])

    @__('integername', 'ID')
    def p_integername(self, p):
        p[0] = (p[1], None)

    # Real
    @__('realdecl', 'REAL', 'realnamelist', 'SEMICOLON')
    def p_realdecl(self, p):
        reallist = [Real(p[1],
                         Width(msb=IntConst('31', lineno=2),
                               lsb=IntConst('0', lineno=2),
                               lineno=2),
                         lineno=2) for r in p[2]]
        p[0] = Decl(tuple(reallist), lineno=1)

    @__('realnamelist', 'realnamelist', 'COMMA', 'realname')
    def p_realnamelist(self, p):
        p[0] = p[1] + (p[3],)

    @__('realnamelist', 'realname')
    def p_realnamelist_one(self, p):
        p[0] = (p[1],)

    @__('realname', 'ID')
    def p_realname(self, p):
        p[0] = p[1]

    # Parameter
    @__('parameterdecl', 'PARAMETER', 'param_substitution_list', 'SEMICOLON')
    def p_parameterdecl(self, p):
        paramlist = [Parameter(rname, rvalue, lineno=2)
                     for rname, rvalue in p[2]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('parameterdecl', 'PARAMETER', 'SIGNED', 'param_substitution_list', 'SEMICOLON')
    def p_parameterdecl_signed(self, p):
        paramlist = [Parameter(rname, rvalue, signed=True, lineno=2)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('parameterdecl', 'PARAMETER', 'width', 'param_substitution_list', 'SEMICOLON')
    def p_parameterdecl_width(self, p):
        paramlist = [Parameter(rname, rvalue, p[2], lineno=3)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('parameterdecl', 'PARAMETER', 'SIGNED', 'width', 'param_substitution_list', 'SEMICOLON')
    def p_parameterdecl_signed_width(self, p):
        paramlist = [Parameter(rname, rvalue, p[3], signed=True, lineno=3)
                     for rname, rvalue in p[4]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('parameterdecl', 'PARAMETER', 'INTEGER', 'param_substitution_list', 'SEMICOLON')
    def p_parameterdecl_integer(self, p):
        paramlist = [Parameter(rname, rvalue, lineno=3)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('localparamdecl', 'LOCALPARAM', 'param_substitution_list', 'SEMICOLON')
    def p_localparamdecl(self, p):
        paramlist = [Localparam(rname, rvalue, lineno=2)
                     for rname, rvalue in p[2]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('localparamdecl', 'LOCALPARAM', 'SIGNED', 'param_substitution_list', 'SEMICOLON')
    def p_localparamdecl_signed(self, p):
        paramlist = [Localparam(rname, rvalue, signed=True, lineno=2)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('localparamdecl', 'LOCALPARAM', 'width', 'param_substitution_list', 'SEMICOLON')
    def p_localparamdecl_width(self, p):
        paramlist = [Localparam(rname, rvalue, p[2], lineno=3)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('localparamdecl', 'LOCALPARAM', 'SIGNED', 'width', 'param_substitution_list', 'SEMICOLON')
    def p_localparamdecl_signed_width(self, p):
        paramlist = [Localparam(rname, rvalue, p[3], signed=True, lineno=3)
                     for rname, rvalue in p[4]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('localparamdecl', 'LOCALPARAM', 'INTEGER', 'param_substitution_list', 'SEMICOLON')
    def p_localparamdecl_integer(self, p):
        paramlist = [Localparam(rname, rvalue, lineno=3)
                     for rname, rvalue in p[3]]
        p[0] = Decl(tuple(paramlist), lineno=1)

    @__('param_substitution_list', 'param_substitution_list', 'COMMA', 'param_substitution')
    def p_param_substitution_list(self, p):
        p[0] = p[1] + (p[3],)

    @__('param_substitution_list', 'param_substitution')
    def p_param_substitution_list_one(self, p):
        p[0] = (p[1],)

    @__('param_substitution', 'ID', 'EQUALS', 'rvalue')
    def p_param_substitution(self, p):
        p[0] = (p[1], p[3])

    @__('assignment', 'ASSIGN', 'lvalue', 'EQUALS', 'rvalue', 'SEMICOLON')
    def p_assignment(self, p):
        p[0] = Assign(p[2], p[4], lineno=1)

    @__('assignment', 'ASSIGN', 'delays', 'lvalue', 'EQUALS', 'delays', 'rvalue', 'SEMICOLON')
    def p_assignment_delay(self, p):
        p[0] = Assign(p[3], p[6], p[2], p[5], lineno=1)

    # --------------------------------------------------------------------------
    @__('lpartselect', 'pointer', 'LBRACKET', 'expression', 'COLON', 'expression', 'RBRACKET')
    def p_lpartselect_lpointer(self, p):
        p[0] = Partselect(p[1], p[3], p[5], lineno=1)

    @__('lpartselect', 'pointer', 'LBRACKET', 'expression', 'PLUSCOLON', 'expression', 'RBRACKET')
    def p_lpartselect_lpointer_plus(self, p):
        p[0] = Partselect(p[1], p[3], Plus(p[3], p[5]), lineno=1)

    @__('lpartselect', 'pointer', 'LBRACKET', 'expression', 'MINUSCOLON', 'expression', 'RBRACKET')
    def p_lpartselect_lpointer_minus(self, p):
        p[0] = Partselect(p[1], p[3], Minus(p[3], p[5]), lineno=1)

    @__('lpartselect', 'identifier', 'LBRACKET', 'expression', 'COLON', 'expression', 'RBRACKET')
    def p_lpartselect(self, p):
        p[0] = Partselect(p[1], p[3], p[5], lineno=1)

    @__('lpartselect', 'identifier', 'LBRACKET', 'expression', 'PLUSCOLON', 'expression', 'RBRACKET')
    def p_lpartselect_plus(self, p):
        p[0] = Partselect(p[1], p[3], Plus(p[3], p[5]), lineno=1)

    @__('lpartselect', 'identifier', 'LBRACKET', 'expression', 'MINUSCOLON', 'expression', 'RBRACKET')
    def p_lpartselect_minus(self, p):
        p[0] = Partselect(p[1], p[3], Minus(p[3], p[5]), lineno=1)

    @__('lpointer', 'pointer')
    def p_lpointer(self, p):
        p[0] = p[1]

    @__('lconcat', 'LBRACE', 'lconcatlist', 'RBRACE')
    def p_lconcat(self, p):
        p[0] = LConcat(p[2], lineno=1)

    @__('lconcatlist', 'lconcatlist', 'COMMA', 'lconcat_one')
    def p_lconcatlist(self, p):
        p[0] = p[1] + (p[3],)

    @__('lconcatlist', 'lconcat_one')
    def p_lconcatlist_one(self, p):
        p[0] = (p[1],)

    @__('lconcat_one', 'identifier')
    def p_lconcat_one_identifier(self, p):
        p[0] = p[1]

    @__('lconcat_one', 'lpartselect')
    def p_lconcat_one_lpartselect(self, p):
        p[0] = p[1]

    @__('lconcat_one', 'lpointer')
    def p_lconcat_one_lpointer(self, p):
        p[0] = p[1]

    @__('lconcat_one', 'lconcat')
    def p_lconcat_one_lconcat(self, p):
        p[0] = p[1]

    @__('lvalue', 'lpartselect')
    def p_lvalue_partselect(self, p):
        p[0] = Lvalue(p[1], lineno=1)

    @__('lvalue', 'lpointer')
    def p_lvalue_pointer(self, p):
        p[0] = Lvalue(p[1], lineno=1)

    @__('lvalue', 'lconcat')
    def p_lvalue_concat(self, p):
        p[0] = Lvalue(p[1], lineno=1)

    @__('lvalue', 'identifier')
    def p_lvalue_one(self, p):
        p[0] = Lvalue(p[1], lineno=1)

    @__('rvalue', 'expression')
    def p_rvalue(self, p):
        p[0] = Rvalue(p[1], lineno=1)

    # --------------------------------------------------------------------------
    # Level 1 (Highest Priority)
    @__('expression', 'MINUS', 'expression %prec', 'UMINUS')
    def p_expression_uminus(self, p):
        p[0] = Uminus(p[2], lineno=1)

    @__('expression', 'PLUS', 'expression %prec', 'UPLUS')
    def p_expression_uplus(self, p):
        p[0] = p[2]

    @__('expression', 'LNOT', 'expression %prec', 'ULNOT')
    def p_expression_ulnot(self, p):
        p[0] = Ulnot(p[2], lineno=1)

    @__('expression', 'NOT', 'expression %prec', 'UNOT')
    def p_expression_unot(self, p):
        p[0] = Unot(p[2], lineno=1)

    @__('expression', 'AND', 'expression %prec', 'UAND')
    def p_expression_uand(self, p):
        p[0] = Uand(p[2], lineno=1)

    @__('expression', 'NAND', 'expression %prec', 'UNAND')
    def p_expression_unand(self, p):
        p[0] = Unand(p[2], lineno=1)

    @__('expression', 'NOR', 'expression %prec', 'UNOR')
    def p_expression_unor(self, p):
        p[0] = Unor(p[2], lineno=1)

    @__('expression', 'OR', 'expression %prec', 'UOR')
    def p_expression_uor(self, p):
        p[0] = Uor(p[2], lineno=1)

    @__('expression', 'XOR', 'expression %prec', 'UXOR')
    def p_expression_uxor(self, p):
        p[0] = Uxor(p[2], lineno=1)

    @__('expression', 'XNOR', 'expression %prec', 'UXNOR')
    def p_expression_uxnor(self, p):
        p[0] = Uxnor(p[2], lineno=1)

    # --------------------------------------------------------------------------
    # Level 2
    @__('expression', 'expression', 'POWER', 'expression')
    def p_expression_power(self, p):
        p[0] = Power(p[1], p[3], lineno=1)

    # --------------------------------------------------------------------------
    # Level 3
    @__('expression', 'expression', 'TIMES', 'expression')
    def p_expression_times(self, p):
        p[0] = Times(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'DIVIDE', 'expression')
    def p_expression_div(self, p):
        p[0] = Divide(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'MOD', 'expression')
    def p_expression_mod(self, p):
        p[0] = Mod(p[1], p[3], lineno=1)

    # --------------------------------------------------------------------------
    # Level 4
    @__('expression', 'expression', 'PLUS', 'expression')
    def p_expression_plus(self, p):
        p[0] = Plus(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'MINUS', 'expression')
    def p_expression_minus(self, p):
        p[0] = Minus(p[1], p[3], lineno=1)

    # --------------------------------------------------------------------------
    # Level 5
    @__('expression', 'expression', 'LSHIFT', 'expression')
    def p_expression_sll(self, p):
        p[0] = Sll(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'RSHIFT', 'expression')
    def p_expression_srl(self, p):
        p[0] = Srl(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'LSHIFTA', 'expression')
    def p_expression_sla(self, p):
        p[0] = Sla(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'RSHIFTA', 'expression')
    def p_expression_sra(self, p):
        p[0] = Sra(p[1], p[3], lineno=1)

    # --------------------------------------------------------------------------
    # Level 6
    @__('expression', 'expression', 'LT', 'expression')
    def p_expression_lessthan(self, p):
        p[0] = LessThan(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'GT', 'expression')
    def p_expression_greaterthan(self, p):
        p[0] = GreaterThan(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'LE', 'expression')
    def p_expression_lesseq(self, p):
        p[0] = LessEq(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'GE', 'expression')
    def p_expression_greatereq(self, p):
        p[0] = GreaterEq(p[1], p[3], lineno=1)

    # --------------------------------------------------------------------------
    # Level 7
    @__('expression', 'expression', 'EQ', 'expression')
    def p_expression_eq(self, p):
        p[0] = Eq(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'NE', 'expression')
    def p_expression_noteq(self, p):
        p[0] = NotEq(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'EQL', 'expression')
    def p_expression_eql(self, p):
        p[0] = Eql(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'NEL', 'expression')
    def p_expression_noteql(self, p):
        p[0] = NotEql(p[1], p[3], lineno=1)

    # --------------------------------------------------------------------------
    # Level 8
    @__('expression', 'expression', 'AND', 'expression')
    def p_expression_And(self, p):
        p[0] = And(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'XOR', 'expression')
    def p_expression_Xor(self, p):
        p[0] = Xor(p[1], p[3], lineno=1)

    @__('expression', 'expression', 'XNOR', 'expression')
    def p_expression_Xnor(self, p):
        p[0] = Xnor(p[1], p[3], lineno=1)

    # --------------------------------------------------------------------------
    # Level 9
    @__('expression', 'expression', 'OR', 'expression')
    def p_expression_Or(self, p):
        p[0] = Or(p[1], p[3], lineno=1)

    # --------------------------------------------------------------------------
    # Level 10
    @__('expression', 'expression', 'LAND', 'expression')
    def p_expression_land(self, p):
        p[0] = Land(p[1], p[3], lineno=1)

    # --------------------------------------------------------------------------
    # Level 11
    @__('expression', 'expression', 'LOR', 'expression')
    def p_expression_lor(self, p):
        p[0] = Lor(p[1], p[3], lineno=1)

    # --------------------------------------------------------------------------
    # Level 12
    @__('expression', 'expression', 'COND', 'expression', 'COLON', 'expression')
    def p_expression_cond(self, p):
        p[0] = Cond(p[1], p[3], p[5], lineno=1)

    # --------------------------------------------------------------------------
    @__('expression', 'LPAREN', 'expression', 'RPAREN')
    def p_expression_expr(self, p):
        p[0] = p[2]

    # --------------------------------------------------------------------------
    @__('expression', 'concat')
    def p_expression_concat(self, p):
        p[0] = p[1]

    @__('expression', 'repeat')
    def p_expression_repeat(self, p):
        p[0] = p[1]

    @__('expression', 'partselect')
    def p_expression_partselect(self, p):
        p[0] = p[1]

    @__('expression', 'pointer')
    def p_expression_pointer(self, p):
        p[0] = p[1]

    @__('expression', 'functioncall')
    def p_expression_functioncall(self, p):
        p[0] = p[1]

    @__('expression', 'systemcall')
    def p_expression_systemcall(self, p):
        p[0] = p[1]

    @__('expression', 'identifier')
    def p_expression_id(self, p):
        p[0] = p[1]

    @__('expression', 'const_expression')
    def p_expression_const(self, p):
        p[0] = p[1]

    @__('concat', 'LBRACE', 'concatlist', 'RBRACE')
    def p_concat(self, p):
        p[0] = Concat(p[2], lineno=1)

    @__('concatlist', 'concatlist', 'COMMA', 'expression')
    def p_concatlist(self, p):
        p[0] = p[1] + (p[3],)

    @__('concatlist', 'expression')
    def p_concatlist_one(self, p):
        p[0] = (p[1],)

    @__('repeat', 'LBRACE', 'expression', 'concat', 'RBRACE')
    def p_repeat(self, p):
        p[0] = Repeat(p[3], p[2], lineno=1)

    @__('partselect', 'identifier', 'LBRACKET', 'expression', 'COLON', 'expression', 'RBRACKET')
    def p_partselect(self, p):
        p[0] = Partselect(p[1], p[3], p[5], lineno=1)

    @__('partselect', 'identifier', 'LBRACKET', 'expression', 'PLUSCOLON', 'expression', 'RBRACKET')
    def p_partselect_plus(self, p):
        p[0] = Partselect(p[1], p[3], Plus(
            p[3], p[5], lineno=1), lineno=1)

    @__('partselect', 'identifier', 'LBRACKET', 'expression', 'MINUSCOLON', 'expression', 'RBRACKET')
    def p_partselect_minus(self, p):
        p[0] = Partselect(p[1], p[3], Minus(
            p[3], p[5], lineno=1), lineno=1)

    @__('partselect', 'pointer', 'LBRACKET', 'expression', 'COLON', 'expression', 'RBRACKET')
    def p_partselect_pointer(self, p):
        p[0] = Partselect(p[1], p[3], p[5], lineno=1)

    @__('partselect', 'pointer', 'LBRACKET', 'expression', 'PLUSCOLON', 'expression', 'RBRACKET')
    def p_partselect_pointer_plus(self, p):
        p[0] = Partselect(p[1], p[3], Plus(
            p[3], p[5], lineno=1), lineno=1)

    @__('partselect', 'pointer', 'LBRACKET', 'expression', 'MINUSCOLON', 'expression', 'RBRACKET')
    def p_partselect_pointer_minus(self, p):
        p[0] = Partselect(p[1], p[3], Minus(
            p[3], p[5], lineno=1), lineno=1)

    @__('pointer', 'identifier', 'LBRACKET', 'expression', 'RBRACKET')
    def p_pointer(self, p):
        p[0] = Pointer(p[1], p[3], lineno=1)

    @__('pointer', 'pointer', 'LBRACKET', 'expression', 'RBRACKET')
    def p_pointer_pointer(self, p):
        p[0] = Pointer(p[1], p[3], lineno=1)

    # --------------------------------------------------------------------------
    @__('const_expression', 'intnumber')
    def p_const_expression_intnum(self, p):
        p[0] = IntConst(p[1], lineno=1)

    @__('const_expression', 'floatnumber')
    def p_const_expression_floatnum(self, p):
        p[0] = FloatConst(p[1], lineno=1)

    @__('const_expression', 'stringliteral')
    def p_const_expression_stringliteral(self, p):
        p[0] = StringConst(p[1], lineno=1)

    @__('floatnumber', 'FLOATNUMBER')
    def p_floatnumber(self, p):
        p[0] = p[1]

    @__('intnumber', ['INTNUMBER_DEC',
                      'SIGNED_INTNUMBER_DEC',
                      'INTNUMBER_BIN',
                      'SIGNED_INTNUMBER_BIN',
                      'INTNUMBER_OCT',
                      'SIGNED_INTNUMBER_OCT',
                      'INTNUMBER_HEX',
                      'SIGNED_INTNUMBER_HEX'])
    def p_intnumber(self, p):
        p[0] = p[1]

    # --------------------------------------------------------------------------
    # String Literal
    @__('stringliteral', 'STRING_LITERAL')
    def p_stringliteral(self, p):
        p[0] = p[1][1:-1]  # strip \" and \"

    # --------------------------------------------------------------------------
    # Always
    @__('always', 'ALWAYS', 'senslist', 'always_statement')
    def p_always(self, p):
        p[0] = Always(p[2], p[3], lineno=1)

    @__('always_ff', 'ALWAYS_FF', 'senslist', 'always_statement')
    def p_always_ff(self, p):
        p[0] = AlwaysFF(p[2], p[3], lineno=1)

    @__('always_comb', 'ALWAYS_COMB', 'senslist', 'always_statement')
    def p_always_comb(self, p):
        p[0] = AlwaysComb(p[2], p[3], lineno=1)

    @__('always_latch', 'ALWAYS_LATCH', 'senslist', 'always_statement')
    def p_always_latch(self, p):
        p[0] = AlwaysLatch(p[2], p[3], lineno=1)

    @__('senslist', 'AT', 'LPAREN', 'edgesigs', 'RPAREN')
    def p_sens_egde_paren(self, p):
        p[0] = SensList(p[3], lineno=1)

    @__('edgesig', 'POSEDGE', 'edgesig_base')
    def p_posedgesig(self, p):
        p[0] = Sens(p[2], 'posedge', lineno=1)

    @__('edgesig', 'NEGEDGE', 'edgesig_base')
    def p_negedgesig(self, p):
        p[0] = Sens(p[2], 'negedge', lineno=1)

    @__('edgesig_base', 'identifier')
    def p_edgesig_base_identifier(self, p):
        p[0] = p[1]

    @__('edgesig_base', 'pointer')
    def p_edgesig_base_pointer(self, p):
        p[0] = p[1]

    @__('edgesigs', 'edgesigs', 'SENS_OR', 'edgesig')
    def p_edgesigs(self, p):
        p[0] = p[1] + (p[3],)

    @__('edgesigs', 'edgesigs', 'COMMA', 'edgesig')
    def p_edgesigs_comma(self, p):
        p[0] = p[1] + (p[3],)

    @__('edgesigs', 'edgesig')
    def p_edgesigs_one(self, p):
        p[0] = (p[1],)

    @__('senslist', 'empty')
    def p_sens_empty(self, p):
        p[0] = SensList((Sens(None, 'all', lineno=1),), lineno=1)

    @__('senslist', 'AT', 'levelsig')
    def p_sens_level(self, p):
        p[0] = SensList((p[2],), lineno=1)

    @__('senslist', 'AT', 'LPAREN', 'levelsigs', 'RPAREN')
    def p_sens_level_paren(self, p):
        p[0] = SensList(p[3], lineno=1)

    @__('levelsig', 'levelsig_base')
    def p_levelsig(self, p):
        p[0] = Sens(p[1], 'level', lineno=1)

    @__('levelsig_base', 'identifier')
    def p_levelsig_base_identifier(self, p):
        p[0] = p[1]

    @__('levelsig_base', 'pointer')
    def p_levelsig_base_pointer(self, p):
        p[0] = p[1]

    @__('levelsig_base', 'partselect')
    def p_levelsig_base_partselect(self, p):
        p[0] = p[1]

    @__('levelsigs', 'levelsigs', 'SENS_OR', 'levelsig')
    def p_levelsigs(self, p):
        p[0] = p[1] + (p[3],)

    @__('levelsigs', 'levelsigs', 'COMMA', 'levelsig')
    def p_levelsigs_comma(self, p):
        p[0] = p[1] + (p[3],)

    @__('levelsigs', 'levelsig')
    def p_levelsigs_one(self, p):
        p[0] = (p[1],)

    @__('senslist', 'AT', 'TIMES')
    def p_sens_all(self, p):
        p[0] = SensList(
            (Sens(None, 'all', lineno=1),), lineno=1)

    @__('senslist', 'AT', 'LPAREN', 'TIMES', 'RPAREN')
    def p_sens_all_paren(self, p):
        p[0] = SensList((Sens(None, 'all', lineno=1),), lineno=1)

    @__('basic_statement', ['if_statement',
                            'case_statement',
                            'casex_statement',
                            'casez_statement',
                            'unique_case_statement',
                            'for_statement',
                            'while_statement',
                            'event_statement',
                            'wait_statement',
                            'forever_statement',
                            'block',
                            'namedblock',
                            'parallelblock',
                            'blocking_substitution',
                            'nonblocking_substitution',
                            'single_statement'])
    def p_basic_statement(self, p):
        p[0] = p[1]

    @__('always_statement', 'basic_statement')
    def p_always_statement(self, p):
        p[0] = p[1]

    # --------------------------------------------------------------------------
    @__('blocking_substitution', 'delays', 'lvalue', 'EQUALS', 'delays', 'rvalue', 'SEMICOLON')
    def p_blocking_substitution(self, p):
        p[0] = BlockingSubstitution(p[2], p[5], p[1], p[4], lineno=2)

    @__('blocking_substitution_base', 'delays', 'lvalue', 'EQUALS', 'delays', 'rvalue')
    def p_blocking_substitution_base(self, p):
        p[0] = BlockingSubstitution(p[2], p[5], p[1], p[4], lineno=2)

    @__('nonblocking_substitution', 'delays', 'lvalue', 'LE', 'delays', 'rvalue', 'SEMICOLON')
    def p_nonblocking_substitution(self, p):
        p[0] = NonblockingSubstitution(
            p[2], p[5], p[1], p[4], lineno=2)

    # --------------------------------------------------------------------------
    @__('delays', 'DELAY', 'LPAREN', 'expression', 'RPAREN')
    def p_delays(self, p):
        p[0] = DelayStatement(p[3], lineno=1)

    @__('delays', 'DELAY', 'identifier')
    def p_delays_identifier(self, p):
        p[0] = DelayStatement(p[2], lineno=1)

    @__('delays', 'DELAY', 'intnumber')
    def p_delays_intnumber(self, p):
        p[0] = DelayStatement(IntConst(p[2], lineno=1), lineno=1)

    @__('delays', 'DELAY', 'floatnumber')
    def p_delays_floatnumber(self, p):
        p[0] = DelayStatement(FloatConst(p[2], lineno=1), lineno=1)

    @__('delays', 'empty')
    def p_delays_empty(self, p):
        p[0] = None

    # --------------------------------------------------------------------------
    @__('block', 'BEGIN', 'block_statements', 'END')
    def p_block(self, p):
        p[0] = Block(p[2], lineno=1)

    @__('block', 'BEGIN', 'END')
    def p_block_empty(self, p):
        p[0] = Block((), lineno=1)

    @__('block_statements', 'block_statements', 'block_statement')
    def p_block_statements(self, p):
        p[0] = p[1] + (p[2],)

    @__('block_statements', 'block_statement')
    def p_block_statements_one(self, p):
        p[0] = (p[1],)

    @__('block_statement', 'basic_statement')
    def p_block_statement(self, p):
        p[0] = p[1]

    # --------------------------------------------------------------------------
    @__('namedblock', 'BEGIN', 'COLON', 'ID', 'namedblock_statements', 'END')
    def p_namedblock(self, p):
        p[0] = Block(p[4], p[3], lineno=1)

    @__('namedblock', 'BEGIN', 'COLON', 'ID', 'END')
    def p_namedblock_empty(self, p):
        p[0] = Block((), p[3], lineno=1)

    @__('namedblock_statements', 'namedblock_statements', 'namedblock_statement')
    def p_namedblock_statements(self, p):
        p[0] = p[1] + (p[2],)

    @__('namedblock_statements', 'namedblock_statement')
    def p_namedblock_statements_one(self, p):
        p[0] = (p[1],)

    @__('namedblock_statement', ['basic_statement',
                                 'decl',
                                 'integerdecl',
                                 'realdecl',
                                 'parameterdecl',
                                 'localparamdecl'])
    def p_namedblock_statement(self, p):  # TODO
        if isinstance(p[1], Decl):
            for r in p[1].list:
                if (not isinstance(r, Reg) and not isinstance(r, Wire) and
                    not isinstance(r, Integer) and not isinstance(r, Real) and
                        not isinstance(r, Parameter) and not isinstance(r, Localparam)):
                    raise ParseError("Syntax Error")
        p[0] = p[1]

    # --------------------------------------------------------------------------
    @__('parallelblock', 'FORK', 'block_statements', 'JOIN')
    def p_parallelblock(self, p):
        p[0] = ParallelBlock(p[2], lineno=1)

    @__('parallelblock', 'FORK', 'JOIN')
    def p_parallelblock_empty(self, p):
        p[0] = ParallelBlock((), lineno=1)

    # --------------------------------------------------------------------------
    @__('if_statement', 'IF', 'LPAREN', 'cond', 'RPAREN', 'true_statement', 'ELSE', 'else_statement')
    def p_if_statement(self, p):
        p[0] = IfStatement(p[3], p[5], p[7], lineno=1)

    @__('if_statement', 'IF', 'LPAREN', 'cond', 'RPAREN', 'true_statement')
    def p_if_statement_woelse(self, p):
        p[0] = IfStatement(p[3], p[5], None, lineno=1)

    @__('if_statement', 'delays', 'IF', 'LPAREN', 'cond', 'RPAREN', 'true_statement', 'ELSE', 'else_statement')
    def p_if_statement_delay(self, p):
        p[0] = IfStatement(p[4], p[6], p[8], lineno=2)

    @__('if_statement', 'delays', 'IF', 'LPAREN', 'cond', 'RPAREN', 'true_statement')
    def p_if_statement_woelse_delay(self, p):
        p[0] = IfStatement(p[4], p[6], None, lineno=2)

    @__('cond', 'expression')
    def p_cond(self, p):
        p[0] = p[1]

    @__('ifcontent_statement', 'basic_statement')
    def p_ifcontent_statement(self, p):
        p[0] = p[1]

    @__('true_statement', 'ifcontent_statement')
    def p_true_statement(self, p):
        p[0] = p[1]

    @__('else_statement', 'ifcontent_statement')
    def p_else_statement(self, p):
        p[0] = p[1]

    # --------------------------------------------------------------------------
    @__('for_statement', 'FOR', 'LPAREN', 'forpre', 'forcond', 'forpost', 'RPAREN', 'forcontent_statement')
    def p_for_statement(self, p):
        p[0] = ForStatement(p[3], p[4], p[5], p[7], lineno=1)

    @__('forpre', 'blocking_substitution')
    def p_forpre(self, p):
        p[0] = p[1]

    @__('forpre', 'SEMICOLON')
    def p_forpre_empty(self, p):
        p[0] = None

    @__('forcond', 'cond', 'SEMICOLON')
    def p_forcond(self, p):
        p[0] = p[1]

    @__('forcond', 'SEMICOLON')
    def p_forcond_empty(self, p):
        p[0] = None

    @__('forpost', 'blocking_substitution_base')
    def p_forpost(self, p):
        p[0] = p[1]

    @__('forpost', 'empty')
    def p_forpost_empty(self, p):
        p[0] = None

    @__('forcontent_statement', 'basic_statement')
    def p_forcontent_statement(self, p):
        p[0] = p[1]

    # --------------------------------------------------------------------------
    @__('while_statement', 'WHILE', 'LPAREN', 'cond', 'RPAREN', 'whilecontent_statement')
    def p_while_statement(self, p):
        p[0] = WhileStatement(p[3], p[5], lineno=1)

    @__('whilecontent_statement', 'basic_statement')
    def p_whilecontent_statement(self, p):
        p[0] = p[1]

    # --------------------------------------------------------------------------
    @__('case_statement', 'CASE', 'LPAREN', 'case_comp', 'RPAREN', 'casecontent_statements', 'ENDCASE')
    def p_case_statement(self, p):
        p[0] = CaseStatement(p[3], p[5], lineno=1)

    @__('casex_statement', 'CASEX', 'LPAREN', 'case_comp', 'RPAREN', 'casecontent_statements', 'ENDCASE')
    def p_casex_statement(self, p):
        p[0] = CasexStatement(p[3], p[5], lineno=1)

    @__('casez_statement', 'CASEZ', 'LPAREN', 'case_comp', 'RPAREN', 'casecontent_statements', 'ENDCASE')
    def p_casez_statement(self, p):
        p[0] = CasezStatement(p[3], p[5], lineno=1)

    @__('unique_case_statement', 'UNIQUE', 'CASE', 'LPAREN', 'case_comp', 'RPAREN', 'casecontent_statements', 'ENDCASE')
    def p_unique_case_statement(self, p):
        p[0] = UniqueCaseStatement(p[3], p[5], lineno=1)

    @__('case_comp', 'expression')
    def p_case_comp(self, p):
        p[0] = p[1]

    @__('casecontent_statements', 'casecontent_statements', 'casecontent_statement')
    def p_casecontent_statements(self, p):
        p[0] = p[1] + (p[2],)

    @__('casecontent_statements', 'casecontent_statement')
    def p_casecontent_statements_one(self, p):
        p[0] = (p[1],)

    @__('casecontent_statement', 'casecontent_condition', 'COLON', 'basic_statement')
    def p_casecontent_statement(self, p):
        p[0] = Case(p[1], p[3], lineno=1)

    @__('casecontent_condition', 'casecontent_condition', 'COMMA', 'expression')
    def p_casecontent_condition_single(self, p):
        p[0] = p[1] + (p[3],)

    @__('casecontent_condition', 'expression')
    def p_casecontent_condition_one(self, p):
        p[0] = (p[1],)

    @__('casecontent_statement', 'DEFAULT', 'COLON', 'basic_statement')
    def p_casecontent_statement_default(self, p):
        p[0] = Case(None, p[3], lineno=1)

    # --------------------------------------------------------------------------
    @__('initial', 'INITIAL', 'initial_statement')
    def p_initial(self, p):
        p[0] = Initial(p[2], lineno=1)

    @__('initial_statement', 'basic_statement')
    def p_initial_statement(self, p):
        p[0] = p[1]

    # --------------------------------------------------------------------------
    @__('event_statement', 'senslist', 'SEMICOLON')
    def p_event_statement(self, p):
        p[0] = EventStatement(p[1], lineno=1)

    # --------------------------------------------------------------------------
    @__('wait_statement', 'WAIT', 'LPAREN', 'cond', 'RPAREN', 'waitcontent_statement')
    def p_wait_statement(self, p):
        p[0] = WaitStatement(p[3], p[5], lineno=1)

    @__('waitcontent_statement', 'basic_statement')
    def p_waitcontent_statement(self, p):
        p[0] = p[1]

    @__('waitcontent_statement', 'SEMICOLON')
    def p_waitcontent_statement_empty(self, p):
        p[0] = None

    # --------------------------------------------------------------------------
    @__('forever_statement', 'FOREVER', 'basic_statement')
    def p_forever_statement(self, p):
        p[0] = ForeverStatement(p[2], lineno=1)

    # --------------------------------------------------------------------------
    @__('instance', 'ID', 'parameterlist', 'instance_bodylist', 'SEMICOLON')
    def p_instance(self, p):
        instancelist = []
        for instance_name, instance_ports, instance_array in p[3]:
            instancelist.append(Instance(p[1], instance_name, instance_ports,
                                         p[2], instance_array, lineno=1))
        p[0] = InstanceList(p[1], p[2], tuple(instancelist), lineno=1)

    @__('instance', 'SENS_OR', 'parameterlist', 'instance_bodylist', 'SEMICOLON')
    def p_instance_or(self, p):
        instancelist = []
        for instance_name, instance_ports, instance_array in p[3]:
            instancelist.append(Instance(p[1], instance_name, instance_ports,
                                         p[2], instance_array, lineno=1))
        p[0] = InstanceList(p[1], p[2], tuple(
            instancelist), lineno=1)

    @__('instance_bodylist', 'instance_bodylist', 'COMMA', 'instance_body')
    def p_instance_bodylist(self, p):
        p[0] = p[1] + (p[3],)

    @__('instance_bodylist', 'instance_body')
    def p_instance_bodylist_one(self, p):
        p[0] = (p[1],)

    @__('instance_body', 'ID', 'LPAREN', 'instance_ports', 'RPAREN')
    def p_instance_body(self, p):
        p[0] = (p[1], p[3], None)

    @__('instance_body', 'ID', 'width', 'LPAREN', 'instance_ports', 'RPAREN')
    def p_instance_body_array(self, p):
        p[0] = (p[1], p[4], p[2])

    @__('instance', 'ID', 'instance_bodylist_noname', 'SEMICOLON')
    def p_instance_noname(self, p):
        instancelist = []
        for instance_name, instance_ports, instance_array in p[2]:
            instancelist.append(Instance(p[1], instance_name, instance_ports,
                                         (), instance_array, lineno=1))
        p[0] = InstanceList(p[1], (), tuple(instancelist), lineno=1)

    @__('instance', 'SENS_OR', 'instance_bodylist_noname', 'SEMICOLON')
    def p_instance_or_noname(self, p):
        instancelist = []
        for instance_name, instance_ports, instance_array in p[2]:
            instancelist.append(Instance(p[1], instance_name, instance_ports,
                                         (), instance_array, lineno=1))
        p[0] = InstanceList(p[1], (), tuple(instancelist), lineno=1)

    @__('instance_bodylist_noname', 'instance_bodylist_noname', 'COMMA', 'instance_body_noname')
    def p_instance_bodylist_noname(self, p):
        p[0] = p[1] + (p[3],)

    @__('instance_bodylist_noname', 'instance_body_noname')
    def p_instance_bodylist_one_noname(self, p):
        p[0] = (p[1],)

    @__('instance_body_noname', 'LPAREN', 'instance_ports', 'RPAREN')
    def p_instance_body_noname(self, p):
        p[0] = ('', p[2], None)

    @__('parameterlist', 'DELAY', 'LPAREN', 'param_args', 'RPAREN')
    def p_parameterlist(self, p):
        p[0] = p[3]

    @__('parameterlist', 'DELAY', 'LPAREN', 'param_args_noname', 'RPAREN')
    def p_parameterlist_noname(self, p):
        p[0] = p[3]

    @__('parameterlist', 'empty')
    def p_parameterlist_empty(self, p):
        p[0] = ()

    @__('param_args_noname', 'param_args_noname', 'COMMA', 'param_arg_noname')
    def p_param_args_noname(self, p):
        p[0] = p[1] + (p[3],)

    @__('param_args_noname', 'param_arg_noname')
    def p_param_args_noname_one(self, p):
        p[0] = (p[1],)

    @__('param_args', 'param_args', 'COMMA', 'param_arg')
    def p_param_args(self, p):
        p[0] = p[1] + (p[3],)

    @__('param_args', 'param_arg')
    def p_param_args_one(self, p):
        p[0] = (p[1],)

    @__('param_args', 'empty')
    def p_param_args_empty(self, p):
        p[0] = ()

    @__('param_arg_noname', 'expression')
    def p_param_arg_noname_exp(self, p):
        p[0] = ParamArg(None, p[1], lineno=1)

    @__('param_arg', 'DOT', 'ID', 'LPAREN', 'expression', 'RPAREN')
    def p_param_arg_exp(self, p):
        p[0] = ParamArg(p[2], p[4], lineno=1)

    @__('instance_ports', ['instance_ports_list', 'instance_ports_arg'])
    def p_instance_ports(self, p):
        p[0] = p[1]

    @__('instance_ports_list', 'instance_ports_list', 'COMMA', 'instance_port_list')
    def p_instance_ports_list(self, p):
        p[0] = p[1] + (p[3],)

    @__('instance_ports_list', 'instance_port_list')
    def p_instance_ports_list_one(self, p):
        p[0] = (p[1],)

    @__('instance_ports_list', 'empty')
    def p_instance_ports_list_empty(self, p):
        p[0] = ()

    @__('instance_port_list', 'expression')
    def p_instance_port_list(self, p):
        p[0] = PortArg(None, p[1], lineno=1)

    @__('instance_ports_arg', 'instance_ports_arg', 'COMMA', 'instance_port_arg')
    def p_instance_ports_arg(self, p):
        p[0] = p[1] + (p[3],)

    @__('instance_ports_arg', 'instance_port_arg')
    def p_instance_ports_arg_one(self, p):
        p[0] = (p[1],)

    @__('instance_port_arg', 'DOT', 'ID', 'LPAREN', 'identifier', 'RPAREN')
    def p_instance_port_arg(self, p):
        p[0] = PortArg(p[2], p[4], lineno=1)

    @__('instance_port_arg', 'DOT', 'ID', 'LPAREN', 'expression', 'RPAREN')
    def p_instance_port_arg_exp(self, p):
        p[0] = PortArg(p[2], p[4], lineno=1)

    @__('instance_port_arg', 'DOT', 'ID', 'LPAREN', 'RPAREN')
    def p_instance_port_arg_none(self, p):
        p[0] = PortArg(p[2], None, lineno=1)

    # --------------------------------------------------------------------------
    @__('genvardecl', 'GENVAR', 'genvarlist', 'SEMICOLON')
    def p_genvardecl(self, p):
        p[0] = Decl(p[2], lineno=1)

    @__('genvarlist', 'genvarlist', 'COMMA', 'genvar')
    def p_genvarlist(self, p):
        p[0] = p[1] + (p[3],)

    @__('genvarlist', 'genvar')
    def p_genvarlist_one(self, p):
        p[0] = (p[1],)

    @__('genvar', 'ID')
    def p_genvar(self, p):
        p[0] = Genvar(name=p[1],
                      width=Width(msb=IntConst('31', lineno=1),
                                  lsb=IntConst('0', lineno=1),
                                  lineno=1),
                      lineno=1)

    @__('generate', 'GENERATE', 'generate_items', 'ENDGENERATE')
    def p_generate(self, p):
        p[0] = GenerateStatement(p[2], lineno=1)

    @__('generate_items', 'empty')
    def p_generate_items_empty(self, p):
        p[0] = ()

    @__('generate_items', 'generate_items', 'generate_item')
    def p_generate_items(self, p):
        p[0] = p[1] + (p[2],)

    @__('generate_items', 'generate_item')
    def p_generate_items_one(self, p):
        p[0] = (p[1],)

    @__('generate_item', ['standard_item', 'generate_if', 'generate_for'])
    def p_generate_item(self, p):
        p[0] = p[1]

    @__('generate_block', 'BEGIN', 'generate_items', 'END')
    def p_generate_block(self, p):
        p[0] = Block(p[2], lineno=1)

    @__('generate_block', 'BEGIN', 'COLON', 'ID', 'generate_items', 'END')
    def p_generate_named_block(self, p):
        p[0] = Block(p[4], p[3], lineno=1)

    @__('generate_if', 'IF', 'LPAREN', 'cond', 'RPAREN', 'gif_true_item', 'ELSE', 'gif_false_item')
    def p_generate_if(self, p):
        p[0] = IfStatement(p[3], p[5], p[7], lineno=1)

    @__('generate_if', 'IF', 'LPAREN', 'cond', 'RPAREN', 'gif_true_item')
    def p_generate_if_woelse(self, p):
        p[0] = IfStatement(p[3], p[5], None, lineno=1)

    @__('gif_true_item', ['generate_item', 'generate_block'])
    def p_generate_if_true_item(self, p):
        p[0] = p[1]

    @__('gif_false_item', ['generate_item', 'generate_block'])
    def p_generate_if_false_item(self, p):
        p[0] = p[1]

    @__('generate_for', 'FOR', 'LPAREN', 'forpre', 'forcond', 'forpost', 'RPAREN', 'generate_forcontent')
    def p_generate_for(self, p):
        p[0] = ForStatement(p[3], p[4], p[5], p[7], lineno=1)

    @__('generate_forcontent', ['generate_item', 'generate_block'])
    def p_generate_forcontent(self, p):
        p[0] = p[1]

    # --------------------------------------------------------------------------
    @__('systemcall', 'DOLLER', 'ID')
    def p_systemcall_noargs(self, p):
        p[0] = SystemCall(p[2], (), lineno=1)

    @__('systemcall', 'DOLLER', 'ID', 'LPAREN', 'sysargs', 'RPAREN')
    def p_systemcall(self, p):
        p[0] = SystemCall(p[2], p[4], lineno=1)

    @__('systemcall', 'DOLLER', 'SIGNED', 'LPAREN', 'sysargs', 'RPAREN')
    def p_systemcall_signed(self, p):  # for $signed system task
        p[0] = SystemCall(p[2], p[4], lineno=1)

    @__('sysargs', 'sysargs', 'COMMA', 'sysarg')
    def p_sysargs(self, p):
        p[0] = p[1] + (p[3],)

    @__('sysargs', 'sysarg')
    def p_sysargs_one(self, p):
        p[0] = (p[1],)

    @__('sysargs', 'empty')
    def p_sysargs_empty(self, p):
        p[0] = ()

    @__('sysarg', 'expression')
    def p_sysarg(self, p):
        p[0] = p[1]

    # --------------------------------------------------------------------------
    @__('function', 'FUNCTION', 'width', 'ID', 'SEMICOLON', 'function_statement', 'ENDFUNCTION')
    def p_function(self, p):
        p[0] = Function(p[3], p[2], p[5], lineno=1)

    @__('function', 'FUNCTION', 'ID', 'SEMICOLON', 'function_statement', 'ENDFUNCTION')
    def p_function_nowidth(self, p):
        p[0] = Function(p[2],
                        Width(IntConst('0', lineno=1),
                              IntConst('0', lineno=1),
                              lineno=1),
                        p[4], lineno=1)

    @__('function', 'FUNCTION', 'INTEGER', 'ID', 'SEMICOLON', 'function_statement', 'ENDFUNCTION')
    def p_function_integer(self, p):
        p[0] = Function(p[3],
                        Width(IntConst('31', lineno=1),
                              IntConst('0', lineno=1),
                              lineno=1),
                        p[5], lineno=1)

    @__('function_statement', 'funcvardecls', 'function_calc')
    def p_function_statement(self, p):
        p[0] = p[1] + (p[2],)

    @__('funcvardecls', 'funcvardecls', 'funcvardecl')
    def p_funcvardecls(self, p):
        p[0] = p[1] + (p[2],)

    @__('funcvardecls', 'funcvardecl')
    def p_funcvardecls_one(self, p):
        p[0] = (p[1],)

    @__('funcvardecl', ['decl', 'integerdecl'])
    def p_funcvardecl(self, p):
        if isinstance(p[1], Decl):
            for r in p[1].list:
                if (not isinstance(r, Input) and not isinstance(r, Reg) and
                        not isinstance(r, Integer)):
                    raise ParseError("Syntax Error")
        p[0] = p[1]

    @__('function_calc', ['blocking_substitution',
                          'if_statement',
                          'for_statement',
                          'while_statement',
                          'case_statement',
                          'casex_statement',
                          'casez_statement',
                          'block',
                          'namedblock'])
    def p_function_calc(self, p):
        p[0] = p[1]

    @__('functioncall', 'identifier', 'LPAREN', 'func_args', 'RPAREN')
    def p_functioncall(self, p):
        p[0] = FunctionCall(p[1], p[3], lineno=1)

    @__('func_args', 'func_args', 'COMMA', 'expression')
    def p_func_args(self, p):
        p[0] = p[1] + (p[3],)

    @__('func_args', 'expression')
    def p_func_args_one(self, p):
        p[0] = (p[1],)

    @__('func_args', 'empty')
    def p_func_args_empty(self, p):
        p[0] = ()

    # --------------------------------------------------------------------------
    @__('task', 'TASK', 'ID', 'SEMICOLON', 'task_statement', 'ENDTASK')
    def p_task(self, p):
        p[0] = Task(p[2], p[4], lineno=1)

    @__('task_statement', 'taskvardecls', 'task_calc')
    def p_task_statement(self, p):
        p[0] = p[1] + (p[2],)

    @__('taskvardecls', 'taskvardecls', 'taskvardecl')
    def p_taskvardecls(self, p):
        p[0] = p[1] + (p[2],)

    @__('taskvardecls', 'taskvardecl')
    def p_taskvardecls_one(self, p):
        p[0] = (p[1],)

    @__('taskvardecls', 'empty')
    def p_taskvardecls_empty(self, p):
        p[0] = ()

    @__('taskvardecl', ['decl', 'integerdecl'])
    def p_taskvardecl(self, p):
        if isinstance(p[1], Decl):
            for r in p[1].list:
                if (not isinstance(r, Input) and not isinstance(r, Reg) and
                        not isinstance(r, Integer)):
                    raise ParseError("Syntax Error")
        p[0] = p[1]

    @__('task_calc', ['blocking_substitution',
                      'if_statement',
                      'for_statement',
                      'while_statement',
                      'case_statement',
                      'casex_statement',
                      'casez_statement',
                      'block',
                      'namedblock'])
    def p_task_calc(self, p):
        p[0] = p[1]

    # --------------------------------------------------------------------------
    @__('identifier', 'ID')
    def p_identifier(self, p):
        p[0] = Identifier(p[1], lineno=1)

    @__('identifier', 'scope', 'ID')
    def p_scope_identifier(self, p):
        p[0] = Identifier(p[2], p[1], lineno=1)

    # --------------------------------------------------------------------------
    @__('scope', 'identifier', 'DOT')
    def p_scope(self, p):
        scope = () if p[1].scope is None else p[1].scope.labellist
        p[0] = IdentifierScope(
            scope + (IdentifierScopeLabel(p[1].name, lineno=1),), lineno=1)

    @__('scope', 'pointer', 'DOT')
    def p_scope_pointer(self, p):
        scope = () if p[1].var.scope is None else p[1].var.scope.labellist
        p[0] = IdentifierScope(scope + (IdentifierScopeLabel(p[1].var.name,
                                                             p[1].ptr, lineno=1),), lineno=1)

    # --------------------------------------------------------------------------
    @__('disable', 'DISABLE', 'ID')
    def p_disable(self, p):
        p[0] = Disable(p[2], lineno=1)

    # --------------------------------------------------------------------------
    @__('single_statement', 'DELAY', 'expression', 'SEMICOLON')
    def p_single_statement_delays(self, p):
        p[0] = SingleStatement(DelayStatement(p[2], lineno=1), lineno=1)

    @__('single_statement', 'systemcall', 'SEMICOLON')
    def p_single_statement_systemcall(self, p):
        p[0] = SingleStatement(p[1], lineno=1)

    @__('single_statement', 'disable', 'SEMICOLON')
    def p_single_statement_disable(self, p):
        p[0] = SingleStatement(p[1], lineno=1)

    # fix me: to support task-call-statement
    # def p_single_statement_taskcall(self, p):
    #    'single_statement : functioncall SEMICOLON'
    #    p[0] = SingleStatement(p[1], lineno=1)

    # def p_single_statement_taskcall_empty(self, p):
    #    'single_statement : taskcall SEMICOLON'
    #    p[0] = SingleStatement(p[1], lineno=1)

    # def p_taskcall_empty(self, p):
    #    'taskcall : identifier'
    #    p[0] = FunctionCall(p[1], (), lineno=1)

    # --------------------------------------------------------------------------
    @__('empty', None)
    def p_empty(self, p):
        pass

    # --------------------------------------------------------------------------
    def error(self, p):
        raise ParseError("%s:" % (p,))
        # self._raise_error(p)

    # --------------------------------------------------------------------------
    def _raise_error(self, p):
        if p:
            msg = 'before: "%s"' % p.value
            coord = self._coord(p.lineno)
        else:
            msg = 'at end of input'
            coord = None

        raise ParseError("%s: %s" % (coord, msg))

    def _coord(self, lineno, column=None):
        ret = [self.filename]
        ret.append('line:%s' % lineno)
        if column is not None:
            ret.append('column:%s' % column)
        return ' '.join(ret)


class ParseError(Exception):
    pass
