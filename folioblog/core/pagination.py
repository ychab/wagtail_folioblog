from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


class FolioBlogPaginator(Paginator):

    def get_page(self, number):
        try:
            number = self.validate_number(number)
        except PageNotAnInteger:
            number = 1
        except EmptyPage:
            return []  # return nothing instead of latests (for infinite-scroll)

        return self.page(number)
