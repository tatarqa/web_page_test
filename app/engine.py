import asyncio
from pyppeteer import launch
from pyppeteer.errors import TimeoutError, PageError
from config_mapping import settings
from logger import Logger
import argparse
import sys


class UnreachableSelector(Exception):
    pass


class Puppeteer(Logger):

    async def __aenter__(self):
        self.browser = await launch()
        self.page = await self.browser.newPage()
        self.pages_history = {}
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.browser.close()

    async def go_to_page(self, url):
        try:
            await self.page.goto(url, waitUntil=['networkidle2', 'load', 'domcontentloaded'], timeout=30000)
        except Exception as e:
            raise Exception(f'Failed to open url {url}, error message is {e}')

    async def click_on_el(self, elem_selector):
        await self.page.click(elem_selector)

    async def check_if_selecotr_is_present(self, elem_selector):
        try:
            await self.page.waitForSelector(elem_selector, timeout=5000)
        except TimeoutError:
            raise UnreachableSelector(
                f'Failed to get HTML element with selector {elem_selector} on page {self.page.url}.')

    async def get_element_js(self, *args):
        # example of usage:
        # await get_element_js('document.getElementsByClassName', 'htmlClass', '.getAttribute("href")', '[0]')
        js_selector_prefix, elem_selector, js_selector_suffix, index = args
        js_expressionx = '''() => {{
            return {{
                result: {0}('{1}'){2}{3},
            }}
        }}'''.format(js_selector_prefix, elem_selector, index, js_selector_suffix)
        elem = await self.page.evaluate(js_expressionx)
        try:
            await self.check_js_query_results(*(elem_selector, elem, self.page.url))
            return elem
        except Exception as e:
            raise e

    async def check_js_query_results(self, *args):
        elem_selector, selected_elem, url = args
        try:
            assert selected_elem is not None

        except AssertionError:
            raise UnreachableSelector(
                f'Failed to get HTML element with selector {elem_selector} on page {url}.')
