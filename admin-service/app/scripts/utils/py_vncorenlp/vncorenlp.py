import jnius_config
import os
import shutil

class VnCoreNLP:
    def __init__(self, max_heap_size='-Xmx2g', annotators=["wseg", "pos", "ner", "parse"], save_dir = './'):
        pwd = os.getcwd()
        if save_dir[-1] == '/':
            save_dir = save_dir[:-1]
        if os.path.isdir(save_dir + "/models") == False or os.path.exists(save_dir + '/VnCoreNLP-1.2.jar') == False:
            raise Exception("Please download the VnCoreNLP model!")
        jnius_config.add_options(max_heap_size)
        self.current_working_dir = os.getcwd()
        os.chdir(save_dir)
        jnius_config.add_classpath('../VnCoreNLP/VnCoreNLP-1.2.jar')
        from jnius import autoclass
        javaclass_vncorenlp = autoclass('vn.pipeline.VnCoreNLP')
        self.javaclass_Annotation = autoclass('vn.pipeline.Annotation')
        self.javaclass_String = autoclass('java.lang.String')
        self.annotators = annotators
        if "wseg" not in annotators:
            self.annotators.append("wseg")

        self.model = javaclass_vncorenlp(annotators)
        os.chdir(pwd)

    def annotate_text(self, text):
        str = self.javaclass_String(text)
        annotation = self.javaclass_Annotation(str)
        self.model.annotate(annotation)
        dict_sentences = {}
        list_sentences = annotation.toString().split("\n\n")[:-1]
        for i in range(len(list_sentences)):
            list_words = list_sentences[i].split("\n")
            list_dict_words = []
            for word in list_words:
                dict_word = {}
                word = word.replace("\t\t", "\t")
                list_tags = word.split("\t")
                dict_word["index"] = int(list_tags[0])
                dict_word["wordForm"] = list_tags[1]
                dict_word["posTag"] = list_tags[2]
                dict_word["nerLabel"] = list_tags[3]
                if "parse" in self.annotators:
                    dict_word["head"] = int(list_tags[4])
                else:
                    dict_word["head"] = list_tags[4]
                dict_word["depLabel"] = list_tags[5]
                list_dict_words.append(dict_word)
            dict_sentences[i] = list_dict_words
        return dict_sentences

    def word_segment(self, text):
        str = self.javaclass_String(text)
        annotation = self.javaclass_Annotation(str)
        self.model.annotate(annotation)
        list_segmented_sentences = []
        list_sentences = annotation.toString().split("\n\n")[:-1]
        for sent in list_sentences:
            list_words = sent.split("\n")
            list_segmented_words = []
            for word in list_words:
                word = word.replace("\t\t", "\t")
                list_tags = word.split("\t")
                list_segmented_words.append(list_tags[1])
            list_segmented_sentences.append(" ".join(list_segmented_words))
        return list_segmented_sentences

    def print_out(self, dict_sentences):
        for sent in dict_sentences.keys():
            list_dict_words = dict_sentences[sent]
            for word in list_dict_words:
                print(str(word["index"]) + "\t" + word["wordForm"] + "\t" + word["posTag"] + "\t" + word["nerLabel"] + "\t" + str(word["head"]) + "\t" + word["depLabel"])
            print("")

    def annotate_file(self, input_file, output_file):
        os.chdir(self.current_working_dir)
        input_str = self.javaclass_String(input_file)
        output_str = self.javaclass_String(output_file)
        self.model.processPipeline(input_str, output_str, self.annotators)

if __name__ == '__main__':
    model = VnCoreNLP(annotators=["wseg"], save_dir='./testvncore')
    output = model.annotate_text("Ông Nguyễn Khắc Chúc  đang làm việc tại Đại học Quốc gia Hà Nội. Bà Lan, vợ ông Chúc, cũng làm việc tại đây.")
    print(output)
    model.print_out(output)
    model.annotate_file(input_file="/home/vinai/Desktop/testvncore/t/input.txt", output_file="output.txt")
    print(model.word_segment("Ông Nguyễn Khắc Chúc  đang làm việc tại Đại học Quốc gia Hà Nội."))