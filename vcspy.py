import os, sys, struct, subprocess



def read_int32(file) -> int:
    entry = file.read(4)
    return struct.unpack('<i', entry)[0]

def read_uint32(file) -> int:
    entry = file.read(4)
    return struct.unpack('<I', entry)[0]

def read_uint16(file) -> int:
    entry = file.read(2)
    return struct.unpack('<H', entry)[0]

def write_Int32(file, int):
    entry = struct.pack('<i', int)
    file.write(entry)


def write_uInt32(file, int):
    entry = struct.pack('<I', int)
    file.write(entry)

#record for one static combo
class StaticComboRecord_t:
    def __init__(self, in_file):
        self.vcs_file = in_file
        self.m_nStaticComboID       = read_uint32(self.vcs_file)          #uint32
        self.m_nFileOffset          = read_uint32(self.vcs_file)          #uint32   


class StaticComboAliasRecord_t:
    def __init__(self, in_file):
        self.vcs_file = in_file
        self.m_nStaticComboID       = read_uint32(self.vcs_file)
        self.m_nSourceStaticCombo   = read_uint32(self.vcs_file)


class SimpleShaderClass:
    def __init__(self, in_file, comboID):
        self.vcs_file = in_file

        shader_found = False

        while not shader_found:
            current_int = read_uint32(self.vcs_file)
            if current_int == 1128421444:
                shader_found = True
        
        if shader_found:

            shader_offset = self.vcs_file.tell() - 16
            self.vcs_file.seek( shader_offset )



        self.combo_subheader_unk1       = read_uint32(self.vcs_file)

        self.vcs_file.seek(self.vcs_file.tell() - 4)

        self.combo_subheader_unk1_part1 = read_uint16(self.vcs_file) 
        self.combo_subheader_unk1_part2 = read_uint16(self.vcs_file)

        self.combo_subheader_comboID    = read_uint32(self.vcs_file)
        self.combo_subheader_filesize   = read_uint32(self.vcs_file)


        self.shader_id = comboID
        self.dwMagicNumber              = read_uint32(self.vcs_file)
        self.dwCheckSum_0               = read_uint32(self.vcs_file)
        self.dwCheckSum_1               = read_uint32(self.vcs_file)
        self.dwCheckSum_2               = read_uint32(self.vcs_file)
        self.dwCheckSum_3               = read_uint32(self.vcs_file)
        self.dwReserved                 = read_uint32(self.vcs_file)
        self.dwSize                     = read_uint32(self.vcs_file)
        self.dwNumChunks                = read_uint32(self.vcs_file)

        self.data = self.vcs_file.read(self.dwSize - 32)

        self.dynamic_combos = []
        self.dynamic_combo_offset_dbg = 0

class VALVECOMPILEDSHADER:

    def __init__( self, in_file ):
        self.vcs_file = in_file

        #header
        #header
        #header

        self.m_nVersion = read_uint32(self.vcs_file)
        
        print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

        if not self.m_nVersion == 6:

            print("Error: Not a valid vcs file")
            print( "Version: " + str(self.m_nVersion) )

            self.is_valid = False
        else:
            self.is_valid = True

            print("VCS IS VALID         //ver 06")
            self.m_nTotalCombos       = read_int32(self.vcs_file)	
            self.m_nDynamicCombos     = read_int32(self.vcs_file)	
            self.m_nFlags             = read_uint32(self.vcs_file)	
            self.m_nCentroidMask      = read_uint32(self.vcs_file)	
            self.m_nNumStaticCombos   = read_uint32(self.vcs_file)	
            self.m_nSourceCRC32	      = read_uint32(self.vcs_file)	

            self.static_combos = []

            for i in range(self.m_nNumStaticCombos):
                self.static_combos.append(StaticComboRecord_t(self.vcs_file))

            self.m_nNumStatic_dupe_record    = read_uint32(self.vcs_file)

            self.static_dupe_records = []

            for i in range(self.m_nNumStatic_dupe_record):
                self.static_dupe_records.append(StaticComboAliasRecord_t(self.vcs_file))
            
            self.static_shaders = []

            first_combo_found = False  

            next_combo_found = False

            for i in range(len(self.static_combos)):
                

                self.vcs_file.seek(self.static_combos[i].m_nFileOffset)
                next_combo_found = False 
                if not first_combo_found:



                    if self.static_combos[i].m_nStaticComboID != 4294967295:
                        current_static_combo = SimpleShaderClass(self.vcs_file, self.static_combos[i].m_nStaticComboID)

                    else: 
                        break
                    if not i + 1 > len(self.static_combos):
                        while not next_combo_found:

                            if self.vcs_file.tell() + 50 > self.static_combos[i + 1].m_nFileOffset :
                                
                                next_combo_found = True
                                

                            else:

                                self.vcs_file.seek(self.vcs_file.tell() - 4)

                                dynamic_offset = self.vcs_file.tell()
                                new_dynamic_combo = SimpleShaderClass(self.vcs_file, 0)
                                new_dynamic_combo.dynamic_combo_offset_dbg = dynamic_offset
                                current_static_combo.dynamic_combos.append(new_dynamic_combo)
                        self.static_shaders.append(current_static_combo)


                







        print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        


def dump_fxc(vcs_class, name):

    static_combo_list = []

    if not os.path.exists('shaders_out'):
        os.makedirs('shaders_out', exist_ok=True)

    for shader_data in vcs_class.static_shaders:
        dynamic_combo_list = []
        shader_file = f'{name}_ID_{shader_data.shader_id}_{shader_data.combo_subheader_unk1}_{shader_data.combo_subheader_comboID}_{len(shader_data.dynamic_combos)}.shdr'
        static_combo_list.append(f"{shader_file}\n")
        with open(f"shaders_out/{shader_file}", "wb") as new_shader_file:

    
            write_uInt32(new_shader_file, shader_data.dwMagicNumber)
            write_uInt32(new_shader_file, shader_data.dwCheckSum_0 )
            write_uInt32(new_shader_file, shader_data.dwCheckSum_1 )
            write_uInt32(new_shader_file, shader_data.dwCheckSum_2 )
            write_uInt32(new_shader_file, shader_data.dwCheckSum_3 )
            write_uInt32(new_shader_file, shader_data.dwReserved   )
            write_uInt32(new_shader_file, shader_data.dwSize       )
            write_uInt32(new_shader_file, shader_data.dwNumChunks  )

            new_shader_file.write(shader_data.data)

        new_shader_file.close()
        dynamic_shader_find_index = 1
        for dynamic_data in shader_data.dynamic_combos:
            
            out_folder = f"shaders_out/{name}_ID_{shader_data.shader_id}_{shader_data.combo_subheader_unk1}_{shader_data.combo_subheader_comboID}_{len(shader_data.dynamic_combos)}/"
            os.makedirs(out_folder, exist_ok=True) 
            dynamic_combo_list.append(f'{dynamic_shader_find_index}_{shader_data.shader_id}_dynamic_{dynamic_data.dynamic_combo_offset_dbg}_{dynamic_data.combo_subheader_unk1}_{dynamic_data.combo_subheader_comboID}.shdr\n')
            with open(f'{out_folder}/{dynamic_shader_find_index}_{shader_data.shader_id}_dynamic_{dynamic_data.dynamic_combo_offset_dbg}_{dynamic_data.combo_subheader_unk1}_{dynamic_data.combo_subheader_comboID}.shdr', "wb") as new_shader_file:

                write_uInt32(new_shader_file, dynamic_data.dwMagicNumber)
                write_uInt32(new_shader_file, dynamic_data.dwCheckSum_0 )
                write_uInt32(new_shader_file, dynamic_data.dwCheckSum_1 )
                write_uInt32(new_shader_file, dynamic_data.dwCheckSum_2 )
                write_uInt32(new_shader_file, dynamic_data.dwCheckSum_3 )
                write_uInt32(new_shader_file, dynamic_data.dwReserved   )
                write_uInt32(new_shader_file, dynamic_data.dwSize       )
                write_uInt32(new_shader_file, dynamic_data.dwNumChunks  )

                new_shader_file.write(dynamic_data.data)

            new_shader_file.close() 
            dynamic_shader_find_index += 1

            with open(f"{out_folder}/dynamic_shader_list.txt", "w") as shader_sl:
                shader_sl.writelines(dynamic_combo_list)

        with open(f"shaders_out/static_shader_list.txt", "w") as shader_sl:
            shader_sl.writelines(static_combo_list)

        with open(f"shaders_out/static_shader.compiled_shader_manifest", "wb") as shader_sl:
            

            write_uInt32(shader_sl, vcs_class.m_nVersion)
            write_Int32(shader_sl, vcs_class.m_nTotalCombos)
            write_Int32(shader_sl, vcs_class.m_nDynamicCombos)
            write_uInt32(shader_sl, vcs_class.m_nFlags)
            write_uInt32(shader_sl, vcs_class.m_nCentroidMask)
            write_uInt32(shader_sl, vcs_class.m_nNumStaticCombos)
            write_uInt32(shader_sl, vcs_class.m_nSourceCRC32)

            #write StaticComboRecord_t

            write_uInt32(shader_sl, vcs_class.m_nNumStatic_dupe_record)

            #write StaticComboAliasRecord_t







def decompile_all():

    for shader_file in os.listdir("shaders_out"):
        subprocess.call(f"fxcd.exe -d shaders_out/{shader_file}")



def pack_vcs(vcs_dir):

    static_combo_list = []

    with open(f"shaders_out/static_shader_list.txt", "r") as shader_sl:

        static_combo_list = shader_sl.readlines()

        for i in range(len(static_combo_list)):

            static_combo_list[i] = static_combo_list[i].strip()

    #calculate the offset of the first combo offset for the first combo record

    first_combo_offset = ( len(static_combo_list) + 1 ) * 8 #static combo list and one extra for the -1 times the bytes for each combo
    first_combo_offset += 32



    with open(f"shaders_out/static_shader.compiled_shader_manifest", "rb") as shader_sl:
        m_nVersion          = read_uint32(shader_sl)
        m_nTotalCombos      = read_int32(shader_sl)
        m_nDynamicCombos    = read_int32(shader_sl)
        m_nFlags            = read_uint32(shader_sl)
        m_nCentroidMask     = read_uint32(shader_sl)
        m_nNumStaticCombos  = read_uint32(shader_sl)    
        m_nSourceCRC32      = read_uint32(shader_sl)  
        
    with open ("shader_out.vcs", "wb") as compiled_shader:

            dynamic_combos = []
            write_uInt32(compiled_shader, m_nVersion)
            write_Int32(compiled_shader,  m_nTotalCombos)
            write_Int32(compiled_shader,  m_nDynamicCombos)
            write_uInt32(compiled_shader, m_nFlags)
            write_uInt32(compiled_shader, m_nCentroidMask)
            write_uInt32(compiled_shader, m_nNumStaticCombos)
            write_uInt32(compiled_shader, m_nSourceCRC32)   


            current_combo_offset = first_combo_offset
            combo_offsets = []
            for i in range(len(static_combo_list)):
                combo_id = static_combo_list[i].split("_")[2]

                offset_filesize = 0

                cached_file_for_size = os.stat(f"{in_dir}/{static_combo_list[i]}")
                static_combo_size = cached_file_for_size.st_size

                if os.path.exists(f"{in_dir}/{static_combo_list[i]}/dynamic_shader_list.txt".replace(".shdr", "")):
                    with open(f"{in_dir}/{static_combo_list[i]}/dynamic_shader_list.txt".replace(".shdr", ""), "r") as dynamic_combo_file:
                        dynamic_combos = dynamic_combo_file.readlines()
                else:
                    dynamic_combos = []
                    for file in dynamic_combos:


                        cached_file_for_size = os.stat(f"{in_dir}/{static_combo_list[i]}/{file}".replace(".shdr", "").replace("\n", "") + ".shdr")
                        static_combo_size += cached_file_for_size.st_size

                combo_list_extradata_size = len(dynamic_combos) * 12
                static_combo_size += combo_list_extradata_size
                static_combo_size += 4

                #we write the record for each static combo
                write_uInt32(compiled_shader, int(combo_id))
                write_uInt32(compiled_shader, current_combo_offset)

                current_combo_offset += static_combo_size

            write_uInt32(compiled_shader, 4294967295)
            final_filesize_offset = compiled_shader.tell()
            write_uInt32(compiled_shader, 3454488)

            #numdupes (not needed?????)
            write_uInt32(compiled_shader, 0)

            #write the static_combo
            for i in range(len(static_combo_list)):


                #block_data_size = 0
                with open(f"{in_dir}/{static_combo_list[i]}", "rb") as static_combo_shdr:

                    split_shader_name = static_combo_list[i].split("_")
   
                    static_combo_shdr.seek(0, os.SEEK_END)
                    size = static_combo_shdr.tell()
                    static_combo_shdr.seek(0)
                    comb_shdr = static_combo_shdr.read()


                    static_combo_shdr.seek(24)

                    combo_offsets.append(compiled_shader.tell())

                    current_block_offset = compiled_shader.tell() #offset of where blocksize is writen

                    write_uInt32(compiled_shader, 6969)
                    write_uInt32(compiled_shader, int(split_shader_name[-2]))
                    write_uInt32(compiled_shader, size)
                    #block_data_size += size
                    compiled_shader.write(comb_shdr)

                #write dynamic combo
                if os.path.exists(f"{in_dir}/{static_combo_list[i]}".replace(".shdr", "")):
                    with open(f"{in_dir}/{static_combo_list[i]}/dynamic_shader_list.txt".replace(".shdr", ""), "r") as dynamic_combo_file:
                        dynamic_combos = dynamic_combo_file.readlines()
                else:
                    dynamic_combos = []

                for dynamic_combo_shdr in dynamic_combos:
                    with open(f"{in_dir}/{static_combo_list[i]}/{dynamic_combo_shdr}".replace(".shdr", "").replace("\n", "") + ".shdr", "rb") as dynamic_combo_shdr:
                        dynam_shdr = dynamic_combo_shdr.read()
                        shader_name_split = f"{in_dir}/{static_combo_list[i]}/{dynamic_combo_shdr}".replace(".shdr", "").replace("\n", "") + ".shdr"
                        shader_name_split = shader_name_split.split("_")
                        dynamic_combo_shdr.seek(24)
                        dynam_filesize = read_uint32(dynamic_combo_shdr)
                        #write the funny 3 ints
                        
                        if not int(shader_name_split[-2]) == 0:

                            current_block_offset_temp = compiled_shader.tell()

                            compiled_shader.seek(current_block_offset)
                            
                            
                            block_data_size = current_block_offset_temp - current_block_offset - 4


                            write_uInt32(compiled_shader, int(block_data_size|0x80000000))


                            current_block_offset = current_block_offset_temp
                            compiled_shader.seek(current_block_offset)

                            write_uInt32(compiled_shader, 69)
                                                    

                        write_uInt32(compiled_shader, int(shader_name_split[-1].replace("'>.shdr","")))
                        write_uInt32(compiled_shader, dynam_filesize)

                        compiled_shader.write(dynam_shdr)

            
                current_block_offset_temp = compiled_shader.tell()
                compiled_shader.seek(current_block_offset)
                block_data_size = current_block_offset_temp - current_block_offset - 4
                write_uInt32(compiled_shader, int(block_data_size|0x80000000))
                current_block_offset = current_block_offset_temp
                compiled_shader.seek(current_block_offset)
                write_uInt32(compiled_shader, 4294967295)


            #seek to filesize offset and set it to current size of file

            compiled_shader.seek(0, os.SEEK_END)
            vcs_size = compiled_shader.tell()
            compiled_shader.seek(final_filesize_offset)
            write_uInt32(compiled_shader, vcs_size)
            
            
            #write the new offsets (hack cause i dont wanna remake the previous shit)

            compiled_shader.seek(28)

            for offset in combo_offsets:
                compiled_shader.seek(compiled_shader.tell() + 4)
                write_uInt32(compiled_shader, offset)
            print('####################################')
            print('#shader packed as "shaders_out.vcs"#')
            print('####################################')

if __name__ == "__main__":

    arguments_list = ["-u", "-p"]

    mode = sys.argv[1]
    in_dir = sys.argv[2]

    if mode == "-u":
        vcs = VALVECOMPILEDSHADER(open(in_dir, "rb"))
        dump_fxc(vcs, "shader")
    elif mode == "-p":
        pack_vcs(in_dir)
