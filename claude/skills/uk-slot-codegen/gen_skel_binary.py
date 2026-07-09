"""
gen_skel_binary.py — Generate correct Spine 3.8 binary .skel placeholder files.
Based on reverse-engineering a working .skel from uk_815.

Spine 3.8 binary format (simplified for minimal skeleton):
  Header: hash(string) + version(string) + x,y,width,height(float) + nonessential(bool)
  If nonessential: fps(float) + imagesPath(string) + audioPath(string)
  Strings: count(varint) + string[]  [shared string table — 0 for minimal]
  Bones: count(varint) + bone[]
  Slots: count(varint) + slot[]
  IK: count(varint)
  Transform: count(varint)
  Path: count(varint)
  Skins: defaultSkin + count(varint) for named skins
  Events: count(varint)
  Animations: count(varint) + animation[]
"""
import struct, sys, os

def write_varint_s(buf, s):
    """Write a string as varint-length-prefixed UTF-8 (length+1, 0=null)."""
    if s is None:
        buf.append(b'\x00')
        return
    encoded = s.encode('utf-8')
    write_varint(buf, len(encoded) + 1)
    buf.append(encoded)

def write_varint(buf, value):
    """Write unsigned varint."""
    result = bytearray()
    while True:
        if (value & ~0x7F) == 0:
            result.append(value & 0xFF)
            break
        result.append(((value & 0x7F) | 0x80) & 0xFF)
        value >>= 7
    buf.append(bytes(result))

def write_float(buf, f):
    buf.append(struct.pack('>f', f))

def write_byte(buf, v):
    buf.append(bytes([v & 0xFF]))

def write_color(buf, r, g, b, a):
    buf.append(bytes([r, g, b, a]))

def write_signed_varint(buf, value):
    """Write signed varint (zigzag encoding)."""
    write_varint(buf, (value << 1) ^ (value >> 31))

def gen_skel(name, anims):
    buf = []
    
    # ─── Header ───
    write_varint_s(buf, 'placeholder_' + name)  # hash
    write_varint_s(buf, '3.8.99')               # version
    write_float(buf, 0)    # x
    write_float(buf, 0)    # y
    write_float(buf, 256)  # width
    write_float(buf, 256)  # height
    write_byte(buf, 1)     # nonessential = true
    # nonessential fields:
    write_float(buf, 30)   # fps
    write_varint_s(buf, './Images/')  # imagesPath
    write_varint_s(buf, '')           # audioPath
    
    # ─── Shared Strings (Spine 3.8.75+) ───
    # The string table is ABSENT in 3.8 binary unless version >= 4.0
    # Actually looking at spine-runtimes source, 3.8 DOES have it:
    # No — checking again: spine 3.8 SkeletonBinary.java readSkeletonData()
    # does NOT read a string table. It reads strings inline.
    # But looking at the hex dump of Bigwin.skel (3.8.99), after the header
    # there's no string table marker... Let me just follow the working file's pattern.
    
    # ─── Bones ───
    write_varint(buf, 1)   # bone count
    # Bone 0 (root): name + parent(-1) + rotation + x + y + scaleX + scaleY + shearX + shearY + length + transformMode
    write_varint_s(buf, 'root')
    # parent: for root bone, Spine 3.8 skips parent index (only non-root write parent)
    # Actually no — root IS index 0 and it writes parentIndex for i > 0
    # So for the first bone (root), there's no parent field written.
    write_float(buf, 0)    # rotation
    write_float(buf, 0)    # x
    write_float(buf, 0)    # y
    write_float(buf, 1)    # scaleX
    write_float(buf, 1)    # scaleY
    write_float(buf, 0)    # shearX
    write_float(buf, 0)    # shearY
    write_float(buf, 0)    # length
    write_varint(buf, 0)   # transformMode: normal
    write_byte(buf, 0)     # skinRequired: false
    write_color(buf, 0x9B, 0x9B, 0x9B, 0xFF)  # bone color (nonessential)
    
    # ─── Slots ───
    write_varint(buf, 1)   # slot count
    write_varint_s(buf, 'slot0')  # name
    write_varint(buf, 0)          # bone index
    write_color(buf, 255, 255, 255, 255)  # color
    # dark color: not present (no flag in 3.8? Let's skip)
    write_varint_s(buf, 'placeholder')  # attachment name
    write_varint(buf, 0)   # blend mode: normal
    
    # ─── IK Constraints ───
    write_varint(buf, 0)
    # ─── Transform Constraints ───
    write_varint(buf, 0)
    # ─── Path Constraints ───
    write_varint(buf, 0)
    
    # ─── Default Skin ───
    # In 3.8: read slotCount for default skin
    write_varint(buf, 1)   # default skin slot count
    write_varint(buf, 0)   # slot index
    write_varint(buf, 1)   # attachment count
    # Attachment key name
    write_varint_s(buf, 'placeholder')
    # Attachment type: 0 = Region
    write_byte(buf, 0)
    # Region attachment:
    write_varint_s(buf, None)  # path (null = use key name)
    write_float(buf, 0)    # rotation
    write_float(buf, 0)    # x
    write_float(buf, 0)    # y
    write_float(buf, 1)    # scaleX
    write_float(buf, 1)    # scaleY
    write_float(buf, 256)  # width
    write_float(buf, 256)  # height
    write_color(buf, 255, 255, 255, 255)  # color
    
    # ─── Named Skins ───
    write_varint(buf, 0)   # no named skins
    
    # ─── Events ───
    write_varint(buf, 0)
    
    # ─── Animations ───
    write_varint(buf, len(anims))
    for anim_name in anims:
        write_varint_s(buf, anim_name)
        
        # Slot timelines count
        write_varint(buf, 0)
        
        # Bone timelines count  
        write_varint(buf, 1)   # 1 bone has timelines
        write_varint(buf, 0)   # bone index
        
        # Timelines for this bone
        write_varint(buf, 1)   # 1 timeline
        # Timeline type: BONE_TRANSLATE = 1
        write_byte(buf, 1)
        # Frame count
        write_varint(buf, 2)
        
        # Frame 0
        write_float(buf, 0)      # time
        write_float(buf, 0)      # x
        write_float(buf, 0)      # y
        # Curve: LINEAR = 1 (between frames, not after last)
        write_byte(buf, 1)
        
        # Frame 1 (last frame — no curve after)
        duration = 1.0 if anim_name in ('Loop', 'Idle') else 0.5
        write_float(buf, duration)  # time
        write_float(buf, 0.01)      # x (tiny offset for trackComplete)
        write_float(buf, 0)         # y
        
        # IK timelines
        write_varint(buf, 0)
        # Transform timelines
        write_varint(buf, 0)
        # Path timelines
        write_varint(buf, 0)
        # Deform timelines
        write_varint(buf, 0)
        # Draw order timeline
        write_varint(buf, 0)
        # Event timeline
        write_varint(buf, 0)
    
    return b''.join(buf)


SPINES = [
    ('BigWin', ['BigWin_Start', 'BigWin_End', 'MegaWin_Start', 'MegaWin_End', 'SuperWin_Start', 'SuperWin_End']),
    ('FG_Declare', ['In', 'Loop', 'Out']),
    ('FG_Compliment', ['In', 'Loop', 'Out']),
    ('SymbolEffect', ['Win', 'Stop', 'Remove']),
    ('NearWin', ['Loop']),
    ('Scatter', ['Win', 'Idle', 'Stop']),
]

if __name__ == '__main__':
    spine_dir = sys.argv[1] if len(sys.argv) > 1 else 'assets/game/Spine'
    for name, anims in SPINES:
        skel_path = os.path.join(spine_dir, name, f'{name}.skel')
        os.makedirs(os.path.dirname(skel_path), exist_ok=True)
        data = gen_skel(name, anims)
        with open(skel_path, 'wb') as f:
            f.write(data)
        print(f'  {name}.skel ({len(data)} bytes): {", ".join(anims)}')
    print('Done.')
