import os
import time
from lex import VerilogLexerPlex as VerilogLexer
from par import VerilogParser


if __name__ == '__main__':
    # par.grammar.print_analysis_table()
    lex = VerilogLexer(error_func=lambda s: print(s))
    with open(os.path.join(__file__, '../verilog_example_1.v')) as fd:
        lex.input(fd.read())
    # lex.input('''
    # module top;
    # reg count;
    # always @* begin
    #     if (1) count = 1;
    #     else count = 0;
    # end
    # endmodule
    # ''')

    # tokens = []
    # for t in lex:
    #     tokens.append(t)
    # print(f'====== tokens ({len(tokens)}) ======')
    # print(tokens)

    par = VerilogParser(debug=True)
    print(par.grammar.stringify_item_collection(par.grammar._itemcol[213]))
    print(par.grammar.stringify_item_collection(par.grammar._itemcol[232]))
    astroot = par.parse(lex)

    astroot.show()

