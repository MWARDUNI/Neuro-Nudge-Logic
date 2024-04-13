
def unpack_cursor(cur):
    res = cur.fetchall()
    if len(res) == 1:
        if len(res[0]) == 1:
            return res[0][0]
        else:
            return list(res[0])
        
    else:
        output = []
        for r in res:
            if len(r) == 1:
                output.append(r[0])
            else:
                output.append(list(r))
        
        return output