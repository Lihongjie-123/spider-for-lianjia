import logging.config
import time
from selenium import webdriver
from optparse import OptionParser
import os
import csv
from src.config.load_config import get_config_map
from selenium.webdriver.common.keys import Keys


workdir = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))  # nopep8
if "lib" == os.path.basename(workdir):
    workdir = os.path.dirname(workdir)
config_map = get_config_map(os.path.join(
                          workdir, 'etc', 'config.conf'))
url_template = "https://cq.lianjia.com/chengjiao/pg%s%s/"


def _handle_cmd_line(args=None):
    parser = OptionParser()

    parser.add_option("--id", dest="id", action="store",
                      type="string", default="0",
                      help="id use guard and create log file")
    parser.add_option("--logconfig", dest="logconfig", action="store",
                      type="string",
                      default=os.path.join(
                          workdir, 'etc', 'log.conf'),
                      help="log config file [%default]")
    (options, args) = parser.parse_args(args=args)
    return options, args


def _valid_options(_options):
    # TODO(lihongjie): 后面可能增加其他参数，用作参数检查
    return True


def main():
    try:
        options, _args = _handle_cmd_line()
        if options.logconfig:
            defaults = {"id": options.id}
            logging.config.fileConfig(options.logconfig, defaults)
        if not _valid_options(options):
            logging.error("options:\n" +
                          '\n'.join('%s = %s' %
                                    (d, getattr(options, d))
                                    for d in options.__dict__))
            return
        driver = \
            webdriver.Chrome(
                executable_path=os.path.join(
                    workdir, 'etc', 'chromedriver.exe')
            )
        for sub_url in config_map["url_array"]:
            output_file_path = \
                os.path.join(workdir, "var", "%s.csv" %
                             config_map["area_array"][
                                 config_map["url_array"].index(sub_url)])
            output_file = open(output_file_path, "a", newline="",
                               encoding="utf-8")
            csv_writer = csv.writer(output_file)
            try:
                logging.info("request url is %s" % sub_url)
                driver.get(sub_url)
                driver.implicitly_wait(100000)
                list_content = driver.find_element_by_class_name("listContent")
                all_info = list_content.find_elements_by_class_name("info")
                for sub_info in all_info:
                    try:
                        deal_date = \
                            sub_info.find_element_by_class_name("dealDate")
                        unit_price = \
                            sub_info.find_element_by_class_name("unitPrice")
                        csv_writer.writerow([deal_date.text, unit_price.text])
                        output_file.flush()
                    except Exception as e:
                        logging.exception(e)
                time.sleep(3)
                page_box = \
                    driver.find_element_by_css_selector(
                        "[class='page-box house-lst-page-box']")
                pagenum = int(str(page_box.text).split(".")[-1][0])
                for index in range(2, pagenum + 1):
                    request_url = \
                        url_template % (
                            index,
                            sub_url.strip("/").split("/")[-1]
                        )
                    driver.get(request_url)
                    driver.implicitly_wait(100000)
                    list_content = driver.find_element_by_class_name(
                        "listContent")
                    all_info = list_content.find_elements_by_class_name("info")
                    for sub_info in all_info:
                        try:
                            deal_date = \
                                sub_info.find_element_by_class_name("dealDate")
                            unit_price = \
                                sub_info.find_element_by_class_name("unitPrice")
                            csv_writer.writerow(
                                [deal_date.text, unit_price.text])
                            output_file.flush()
                        except Exception as e:
                            logging.exception(e)
                time.sleep(3)
            except Exception as e:
                logging.exception(e)
            driver.close()
            output_file.close()

    except Exception as e:
        logging.exception(e)


if __name__ == "__main__":
    try:
        old_time = time.time()
        main()
        new_time = time.time()
        print(new_time - old_time)
    except Exception as ex:
        logging.exception(ex)
        exit(-1)
